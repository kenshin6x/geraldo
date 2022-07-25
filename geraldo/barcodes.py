"""Module with BarCodes functions on Geraldo."""

from .graphics import Graphic
from .utils import memoize, get_attr_value, cm

from reportlab.graphics.barcode import getCodeNames
from reportlab.graphics.barcode.common import Codabar, Code11, I2of5, MSI
from reportlab.graphics.barcode.code128 import Code128
from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget, Ean8BarcodeWidget
from reportlab.graphics.barcode.code39 import Extended39, Standard39
from reportlab.graphics.barcode.code93 import Extended93, Standard93
from reportlab.graphics.barcode.usps import FIM, POSTNET
from reportlab.graphics.barcode.usps4s import USPS_4State
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.barcode import createBarcodeDrawing

SUPPORTED_BARCODE_TYPES = getCodeNames()
BARCODE_CLASSES = {
    'Codabar': Codabar,
    'Code11': Code11,
    'Code128': Code128,
    'EAN13': Ean13BarcodeWidget,
    'EAN8': Ean8BarcodeWidget,
    'Extended39': Extended39,
    'Extended93': Extended93,
    'FIM': FIM,
    'I2of5': I2of5,
    'MSI': MSI,
    'POSTNET': POSTNET,
    'Standard39': Standard39,
    'Standard93': Standard93,
    'USPS_4State': USPS_4State,
    'QR': QrCodeWidget,
}


class BarCode(Graphic):
    """Class used by all barcode types generation. A barcode is just another graphic
    element, with basic attributes, like 'left', 'top', 'width', 'height' and
    'visible', plus its specific attributes 'type', 'checksum' and 'attribute_name' -
    the last one seemed to the similar from ObjectValue.

    The attribute 'width' is not about the graphic width, but the bar width (what
    means you must have a value like 0.01*cm or less to have a good result).

    Another attribute is 'routing_attribute' used only by type 'USPS_4State'.

    Also supports 'get_value' lambda attribute, like ObjectValue (with the argument
    'inst')"""

    _type = None
    _width = 0.03*cm
    _height = 1.5*cm
    attribute_name = None
    checksum = 0
    routing_attribute = None
    aditional_barcode_params = {}
    get_value = None # A lambda function to get customized values
    
    #QRCode
    qr_level = 'L'
    border   = 4

    def clone(self):
        new = super(BarCode, self).clone()

        new.type = self.type
        new.attribute_name = self.attribute_name
        new.get_value = self.get_value
        new.checksum = self.checksum
        new.routing_attribute = self.routing_attribute
        new.aditional_barcode_params = self.aditional_barcode_params
        
        new.qr_level = self.qr_level
        new.border   = self.border

        return new

    def set_type(self, typ):
        if typ not in SUPPORTED_BARCODE_TYPES:
            raise Exception('Supported types are: '+', '.join(SUPPORTED_BARCODE_TYPES))

        self._type = typ
    type = property(lambda self: self._type, set_type)

    def render(self):
        if not getattr(self, '_rendered_drawing', None):
            kwargs = self.aditional_barcode_params
            kwargs['value'] = self.get_object_value()
            
            if 'barWidth' not in kwargs:
                kwargs['barWidth'] = self.width

            if 'barHeight' not in kwargs:
                kwargs['barHeight'] = self.height
            
            ##QRCode
            if 'barLevel' not in kwargs:
                kwargs['barLevel'] = self.qr_level
                
            if 'barBorder' not in kwargs:
                kwargs['barBorder'] = self.border
            ####
                
            if self.type in ('EAN13','EAN8','QR'):
                self._rendered_drawing = createBarcodeDrawing(self.type, **kwargs)
            else:
                cls = BARCODE_CLASSES[self.type]

                kwargs['checksum'] = self.checksum

                if self.type in ('USPS_4State',):
                    kwargs['routing'] = get_attr_value(self.instance, self.routing_attribute)

                self._rendered_drawing = cls(**kwargs)

        return self._rendered_drawing

    def get_object_value(self, instance=None):
        """Return the attribute value for just an object"""

        instance = instance or self.instance

        if self.get_value and instance:
            return self.get_value(instance)

        value = get_attr_value(instance, self.attribute_name)

        return value

    def _get_width(self):
        drawing = getattr(self, '_rendered_drawing', None)
        return drawing and drawing.width or self._width

    def _set_width(self, value):
        self._width = value

    width = property(_get_width, _set_width)
    