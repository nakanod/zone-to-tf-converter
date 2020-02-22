#!/usr/bin/env python

import sys

import dns.zone
import dns.rdatatype
from jinja2 import Environment, FileSystemLoader


class Route53Record(object):
    def __init__(self, origin, name, rdataset, zone_defined_name):
        self.rdata = []
        self.rdtype = dns.rdatatype.to_text(rdataset.rdtype)
        self.ttl = int(rdataset.ttl)
        self.zone_id = 'aws_route53_zone.{}.zone_id'.format(zone_defined_name)
        origin_hyphen = origin[:-1].replace('.', '-')
        sub_domain = str(name)
        naked_domain = 'aws_route53_zone.{}.name'.format(zone_defined_name)
        if sub_domain == '@':
            self.name = naked_domain
            self.defined_name = '{}-{}'.format(self.rdtype.lower(), origin_hyphen)
        else:
            self.name = '"{}.${{{}}}"'.format(sub_domain, naked_domain)
            self.defined_name = '{}-{}-{}'.format(self.rdtype.lower(), sub_domain.replace('.', '-'), origin_hyphen)
        if self.rdtype == 'TXT':
            self.rdata = ['{}'.format(rdata.to_text()) for rdata in rdataset]
        else:
            self.rdata = ['"{}"'.format(rdata.to_text().replace('"', '\\"')) for rdata in rdataset]


class Route53Zone(object):
    def __init__(self, filename):
        self.rdataset = []
        zone = dns.zone.from_file(filename)
        self.origin = str(zone.origin)
        self.defined_name = 'zone-{}'.format(self.origin[:-1].replace('.', '-'))
        self.rdataset = [Route53Record(self.origin, name, rdataset, self.defined_name) for name, node in zone.nodes.items() for rdataset in node.rdatasets]


def help():
    print("error: {} needs 1 argument that is a dns zone file.".format(sys.argv[0]))
    print("usage: {} ZONEFILE".format(sys.argv[0]))


def main():
    if len(sys.argv) != 2:
        help()
        return

    zonefile = sys.argv[1]
    zone = Route53Zone(zonefile)
    loader = FileSystemLoader("templates")
    env = Environment(loader=loader)
    template = env.get_template('route53.tf.j2')
    render = template.render(zone=zone)

    print(render)


if __name__ == '__main__':
    main()
