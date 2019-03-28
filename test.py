from dm_map_pages import dm_map_pages

dm_list = dm_map_pages()

with open("dm_mapped_pages.txt","w") as f:
    for item in dm_list:
        f.write("%s\n" % item)
