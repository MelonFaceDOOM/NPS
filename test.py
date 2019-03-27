from dm_map_pages import dm_map_pages
from tor_session import DmSession

ds = DmSession()

urls = dm_map_pages()
print(urls[:10])