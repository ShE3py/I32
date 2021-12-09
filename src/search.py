import database


def do_search(query_vars: dict[str, list[str]]) -> str:
    search_input = query_vars['s'][0]

    text = ""
    with database.conn.cursor() as cursor:
        cursor.execute("SELECT * FROM recherche(%s)", ('%' + search_input + '%',))

        for record in cursor:
            text += "Modèle: {}<br />" \
                    "Catégorie: {}<br />" \
                    "Vendeur: {} {}<br />" \
                    "Prix: {}€<br />" \
                .format(record[0], record[1], record[3], record[4], record[2])

    return text


















