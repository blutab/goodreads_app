import urllib.request

def get_user_data(
    user_id, key="ZRnySx6awjQuExO9tKEJXw", v="2", shelf="read", per_page="200"
):
    api_url_base = "https://www.goodreads.com/review/list/"
    final_url = (
        api_url_base
        + user_id
        + ".xml?key="
        + key
        + "&v="
        + v
        + "&shelf="
        + shelf
        + "&per_page="
        + per_page
    )
    contents = urllib.request.urlopen(final_url).read()
    return contents

