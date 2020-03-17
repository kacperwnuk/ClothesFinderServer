import itertools
from multiprocessing import Pool
from ClothesSearchApp.scrappers.RESERVEDScrapper import RESERVEDScrapper
from ClothesSearchApp.scrappers.HMScrapper import HMScrapper
from ClothesSearchApp.scrappers.HOUSEScrapper import HOUSEScrapper
from ClothesSearchApp.scrappers.defaults import transform_request

scrapper_mapping = {
    'HM': HMScrapper,
    'HOUSE': HOUSEScrapper,
    'RESERVED': RESERVEDScrapper,
}

detailed_request_hm = {
    'id': '0684021066',
    'shop': 'HM',
}

detailed_request_reserved = {
    'id': 'xk836-59x',
    'shop': 'RESERVED',
}

detailed_request_house = {
    # 'id': 'yu781-01x',
    'id': 'yf626-85m',
    'shop': 'HOUSE',
}

# request = {
#     'sort_type': 2,
#     'size': 'M',
#     'type': 'Marynarki'
# }

request = {
    'sort_type': 2,
    'size': 'M',
    'type': 'T-Shirty'
}

transformed_request = transform_request(request)
scrapper_classes = [HMScrapper, HOUSEScrapper, RESERVEDScrapper]


def create_scrappers(scrapper_classes):
    return [scrapper_class() for scrapper_class in scrapper_classes if
            transformed_request['type'] in scrapper_class.clothes_type_class.clothes_types]


def find_clothes():
    scrappers = create_scrappers(scrapper_classes)
    clothes = [scrapper.retrieve_general_data(transformed_request) for scrapper in scrappers]
    clothes = list(itertools.chain(*clothes))
    return clothes
    # print(clothes)


def find_info(detailed_request):
    scrapper = scrapper_mapping[detailed_request['shop']]()
    clothes_info = scrapper.get_clothes_type_detailed_data(detailed_request['id'])
    return clothes_info
    # print(clothes_info.json())


if __name__ == '__main__':
    # find_clothes()
    # rs = RESERVEDScrapper()
    rs = HMScrapper()
    clothes = rs.get_clothes_type_general_data(transformed_request)

    # clothes = find_clothes()
    ids = [cloth.id for cloth in clothes]
    print(ids)

    from time import perf_counter

    t1 = perf_counter()
    p = Pool(3)
    p.map(rs.get_clothes_type_detailed_data, ids)
    p.terminate()
    p.join()
    t2 = perf_counter()
    print(t2 - t1)
    info = []
    # for id in ids:
    #     cloth_info = rs.get_clothes_type_detailed_data(id)
    #     info.append(rs.get_clothes_type_detailed_data(id).json())
    #     # print(cloth_info.json())
    # print(info)

    # print(find_info(detailed_request_reserved).json())
    # RESERVEDScrapper(transformed_request).retrieve_general_data()

    # retrieve_data(clothes_types, request)
    # HMScrapper(transform_request(request)).retrieve_data()
