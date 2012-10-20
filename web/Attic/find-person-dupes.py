munis = Municipality.objects.all()

for muni in munis:
    p_list = Person.objects.filter(municipality=muni).order_by('last_name', 'first_name')
    old_p = None
    for p in p_list:
        if old_p and p.last_name == old_p.last_name and p.first_name == old_p.first_name:
            print p
            p.delete()
            old_p.delete()
            old_p = None
        old_p = p

