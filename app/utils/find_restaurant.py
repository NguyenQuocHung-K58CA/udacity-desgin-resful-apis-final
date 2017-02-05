from geocode import get_geocode_location
import json
import httplib2

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

foursquare_client_id = "1KMQEY5XSNAX4JIDJUEXT4LR21WLL3HRFQJ3CKWEU4FE1SYU"
foursquare_client_secret = "MAMSSXHUGF25CAWACUKDIGJZ4ICP00TUEB1YOXIQNNPR14JT"


def find_restaurant(mealType,location):
    latitude, longitude = get_geocode_location(location)

    # 2. Use foursquare API to find a nearby restaurant with the latitude, longitude, and mealType strings.
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20130815&ll=%s,%s&query=%s'
           % (foursquare_client_id, foursquare_client_secret, latitude, longitude, mealType))
    h = httplib2.Http()
    result = json.loads(h.request(url, method="GET")[1])

    if result['response']['venues']:
        venue = result['response']['venues'][0]
        venue_id = venue['id']
        venue_name = venue['name']
        venue_address = ' '.join( venue['location']['formattedAddress'] )

        url = ('https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&client_secret=%s&v=20150603'
               % (venue_id, foursquare_client_id, foursquare_client_secret))

        content = json.loads( h.request(url, method="GET")[1] )

        if content['response']['photos']['items']:
            photo = content['response']['photos']['items'][0]
            prefix = photo['prefix']
            suffix = photo['suffix']
            image_url = prefix + "300*300" + suffix
        else:
            image_url = "a.jpg"

        restaurant = {
            'name': venue_name,
            'address': venue_address,
            'image_url': image_url
        }

        return restaurant

    else:
        print 'Can not find a suitable restaurant'
        return 'No restaurant found'
