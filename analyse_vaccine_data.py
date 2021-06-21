from read_vaccine_data import read_vaccine_data
import numpy as np


def save_individual_country(country_name, colour, per_hundred=True):
    vac = vac_data.read_single_country(country_name)
    pop = vac_data.calc_population(country_name)
    vac_data.save_data(vac, 1, country_name)
    np.savetxt('../result/'+country_name+'_pop.txt', [pop])


def save_multi_countries(countries, label, colour, per_hundred=True):
    vac = vac_data.read_multi_countries(countries)
    pop = vac_data.calc_population(countries)
    vac_data.save_data(vac, 1, label)
    np.savetxt('../result/'+label+'_pop.txt', [pop])


vac_data = read_vaccine_data()

# Analyse individual countries
# save_individual_country('Mexico', 'red', per_hundred=True)
# save_individual_country('United States', 'blue', per_hundred=True)

# Analyse a collection of countries
countries = vac_data.list_countries()
HIC, LMIC, UNK = vac_data.sort_countries_by_income(countries)
save_multi_countries(LMIC, 'LMIC', 'red', per_hundred=True)
save_multi_countries(HIC, 'HIC', 'blue', per_hundred=True)
