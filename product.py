#This file is part product_name module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Product']
__metaclass__ = PoolMeta

STATES = {
    'readonly': ~Eval('active', True),
    'invisible': (~Eval('variant_name', False) & Eval('_parent_template', {}).get('unique_variant', False)),
    'required': ~(Eval('variant_name', False) | Eval('_parent_template', {}).get('unique_variant', False)),
    }
DEPENDS = ['active']


class Product:
    __name__ = 'product.product'
    name = fields.Char("Name", size=None, select=True, states=STATES,
        depends=DEPENDS)
    variant_name = fields.Function(fields.Boolean('Variant Name'),
        'on_change_with_variant_name')

    def __getattr__(self, name):
        result = super(Product, self).__getattr__(name)
        if not result and name == 'name':
            return getattr(self.template, name)
        return result

    @fields.depends('template')
    def on_change_with_variant_name(self, name=None):
        if self.template:
            return self.template.unique_variant
        return False

    @classmethod
    def search(cls, domain, offset=0, limit=None, order=None, count=False,
            query=False):
        for d in domain:
            if d and d[0] == 'name':
                domain = ['OR', domain[:], ('template.name', 'ilike', d[2])]
                break
        return super(Product, cls).search(domain, offset=offset, limit=limit,
            order=order, count=count, query=query)

    @classmethod
    def search_rec_name(cls, name, clause):
        res = super(Product, cls).search_rec_name(name, clause)
        return ['OR',
            res,
            [('name', ) + tuple(clause[1:])]
            ]

    def get_rec_name(self, name):
        if self.code and self.name:
            return '[' + self.code + '] ' + self.name
        elif self.code:
            return '[' + self.code + '] ' + self.template.name
        else:
            return self.template.name
