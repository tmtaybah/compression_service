# -*- coding: utf-8 -*-

import random
from compression_service.compress import compress, decompress


def test_compress():
    '''
    test compress function with selected strings
    '''

    invalid = 'Invalid: contains non-lowercase characters'

    test_cases = [('a', 'a'), ('aa', 'aa'), ('aaaaa', '5a'),
                  ('abcdefg', 'abcdefg'), ('aaaccddddhhhhi', '3acc4d4hi'),
                  ('aaaaabbbbbbaaabb', '5a6b3abb'), ('123', invalid),
                  ('zasfd@@', invalid), ('AASSSDDDFGHJHGFSDFDGFHGCKY????????',
                  invalid)]

    for case in test_cases:
        assert compress(case[0]) == case[1]
