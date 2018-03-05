def n4j_dict_format(query):
    s_query = "{{{}}}"
    kv_pairs = ""
    key_val = "{}:'{}'"
    for k,v in query.items():
        try:
            kv_pairs = kv_pairs + "," + key_val.format(k, v)
        except Exception:
            pass
    s_query = s_query.format(kv_pairs[1:])
    return s_query
