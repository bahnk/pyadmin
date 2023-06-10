
# coding: utf-8

import libtorrent as lt

ses = lt.session()

e = lt.bdecode(open("test.torrent", 'rb').read())
info = lt.torrent_info(e)
