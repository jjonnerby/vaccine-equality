import pandas as pd
import numpy as np
from datetime import datetime
import country_converter as coco


class read_vaccine_data():
    def __init__(self):
        """Read vaccination data, collected from Our World in Data. Also reads
        population sizes and income brackets of each country using data from
        the World Bank.

        """
        vaccine_file = '../data/vaccinations.json'
        population_file = '../data/API_SP.POP.TOTL_DS2_en_csv_v2_2252106.csv'
        self.countries_file = '../data/country.csv'
        self.incomes_file = '../data/Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_2252106.csv'

        self.df_Vac = pd.read_json(vaccine_file)
        self.df_Pop = pd.read_csv(population_file, header=2)

    def read_single_country(self, country_name):
        """Returns a dataframe with daily and total vaccinations in a country
        """
        single_country = self.df_Vac['country'] == country_name

        Ndays = len(self.df_Vac[single_country]['data'].iloc[0])
        vacc_date = []
        daily_vacc = []
        for i in range(1, Ndays):
            vacc_date.append(
                datetime.strptime(
                    self.df_Vac[single_country]['data'].iloc[0][i]['date'],
                    '%Y-%m-%d').date())
            try:
                daily_vacc.append(
                    self.df_Vac[single_country]['data'].iloc[0][i][
                        'daily_vaccinations'])
            except:
                print('Exception raised')
                # Need to investigate further!
                daily_vacc.append(0)

        total = np.cumsum(daily_vacc)
        d = {'date': vacc_date, 'daily': daily_vacc,
             'total': total}
        return pd.DataFrame(data=d)

    def _merge_two_countries(self, df1, df2):
        """Merge two countries into a single dataframe"""
        df = pd.merge(df1, df2, how='outer', on='date').fillna(0)
        daily = df['daily_x'] + df['daily_y']
        d = {'date': df['date'], 'daily': daily}
        df3 = pd.DataFrame(d).sort_values(by='date')
        df3['total'] = np.cumsum(df3['daily'])
        return df3

    def read_multi_countries(self, countries):
        """Read a list of country names, return a dataframe with daily and total
        vaccinations performed"""
        df = self.read_single_country(countries[0])

        for country_name in countries[1:]:
            df = self._merge_two_countries(
                df, self.read_single_country(country_name))
        return df

    def multi_countries_total(self, countries):
        """Returns a dataframe with the total number of vaccinations performed
        in the list of countries provided
        """
        df = self.read_single_country(countries[0])
        try:
            total = df['total'].iloc[-1]
        except:
            total = 0
        df2 = pd.DataFrame(
            {'country': countries[0], 'total': total}, index=[0])
        for country_name in countries[1:]:
            df = self.read_single_country(country_name)
            try:
                total = df['total'].iloc[-1]
            except:
                total = 0
            df2 = df2.append(
                {'country': country_name, 'total': total}, ignore_index=True)
        return df2

    def list_countries(self):
        """Filters out real countries from aggregates (Africa, Arab world, etc.)
        """
        df = pd.read_csv(self.countries_file)
        df = df.rename(columns={'value': 'country'})

        df2 = pd.merge(
            df, self.df_Vac, on=['country'], how='left', indicator='Exist')
        df2['Exist'] = np.where(df2.Exist == 'both', True, False)
        return df2[df2['Exist']]['country']

    def sort_countries_by_income(self, countries):
        """Uses World Bank data to sort countries by income"""
        df = pd.read_csv(self.incomes_file)
        HIC = []
        LMIC = []
        UNK = []
        for country_name in countries:
            country_code = coco.convert(names=country_name, to='ISO3')
            try:
                income = df[
                    df['Country Code'] == country_code].iloc[0]['IncomeGroup']
                if income == 'High income':
                    HIC.append(country_name)
                else:
                    LMIC.append(country_name)
            except:
                UNK.append(country_name)
        return HIC, LMIC, UNK

    def calc_population(self, countries):
        """Calculate the population in a single country, or the sum of
        several countries in a list"""
        if not (
                isinstance(
                    countries, pd.Series) or isinstance(
                        countries, list)):
            countries = [countries]
        df = pd.DataFrame({'Country Name': countries})
        dfp = pd.merge(
            self.df_Pop, df, on=['Country Name'], how='left',
            indicator='Exist')
        return np.sum(dfp[np.where(dfp.Exist == 'both', True, False)]['2019'])

    def save_data(self, data, factor, label):
        df = data
        df['daily'] = df['daily']/factor
        df['total'] = df['total']/factor
        df.to_csv('../result/'+label+'.csv')
