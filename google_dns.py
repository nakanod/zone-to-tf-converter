#!/usr/bin/env python

import sys

import dns.zone
import dns.rdatatype


def help():
    print("error: {} needs 1 argument that is a dns zone file.".format(sys.argv[0]))
    print("usage: {} ZONEFILE".format(sys.argv[0]))


def main():
    if len(sys.argv) != 2:
        help()
        return

    zonefile = sys.argv[1]
    zone = dns.zone.from_file(zonefile)
    managed_zone_dns_name = str(zone.origin)
    origin_hyphen = managed_zone_dns_name[:-1].replace(".", "-")
    managed_zone_variable = 'zone-{}'.format(origin_hyphen)

    managed_zone_string = 'resource "google_dns_managed_zone" "{}" {{\n'.format(managed_zone_variable)
    managed_zone_string += '  name = "{}"\n'.format(managed_zone_variable)
    managed_zone_string += '  dns_name = "{}"\n'.format(managed_zone_dns_name)
    managed_zone_string += '  visibility = "public"\n'
    managed_zone_string += '}\n'
    print(managed_zone_string)

    naked_domain = "google_dns_managed_zone.{}.dns_name".format(managed_zone_variable)

    for name, node in zone.nodes.items():
        for rdataset in node.rdatasets:
            rdtype = dns.rdatatype.to_text(rdataset.rdtype)
            ttl = rdataset.ttl
            sub_domain = str(name)
            rrdatas = ''

            if rdtype == 'SOA' or rdtype == 'NS':
                continue

            for rdata in rdataset:
                rrdatas += '"{}",'.format(rdata.to_text().replace('"', '\\"'))

            if sub_domain == '@':
                name_string = '{}'.format(naked_domain)
                record_set_variable = '{}-{}'.format(rdtype.lower(), origin_hyphen)
                pass
            else:
                name_string = '"{}.${{{}}}"'.format(sub_domain, naked_domain)
                record_set_variable = '{}-{}-{}'.format(rdtype.lower(), sub_domain.replace(".", "-"), origin_hyphen)
                pass

            record_set_string = 'resource "google_dns_record_set" "{}" {{\n'.format(record_set_variable)
            record_set_string += '  type = "{}"\n'.format(rdtype)
            record_set_string += '  ttl = {}\n'.format(ttl)
            record_set_string += '  name = {}\n'.format(name_string)
            record_set_string += '  managed_zone = google_dns_managed_zone.{}.name\n'.format(managed_zone_variable)
            record_set_string += '  rrdatas = [{}]\n'.format(rrdatas)
            record_set_string += '}\n'
            print(record_set_string)


if __name__ == '__main__':
    main()
