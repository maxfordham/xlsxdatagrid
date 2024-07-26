# generated by datamodel-codegen:
#   filename:  frictionless.schema.json
#   timestamp: 2024-06-09T14:09:36+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, constr


class Type(Enum):
    string = 'string'


class Format(Enum):
    default = 'default'
    email = 'email'
    uri = 'uri'
    binary = 'binary'
    uuid = 'uuid'


class Constraints(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    pattern: Optional[str] = Field(
        None,
        description='A regular expression pattern to test each value of the property against, where a truthy response indicates validity.',
    )
    enum: Optional[List[str]] = Field(None, min_items=1, unique_items=True)
    minLength: Optional[int] = Field(
        None, description='An integer that specifies the minimum length of a value.'
    )
    maxLength: Optional[int] = Field(
        None, description='An integer that specifies the maximum length of a value.'
    )


class Fields(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Optional[Type] = Field(
        None, description='The type keyword, which `MUST` be a value of `string`.'
    )
    format: Optional[Format] = Field(
        'default',
        description='The format keyword options for `string` are `default`, `email`, `uri`, `binary`, and `uuid`.',
    )
    constraints: Optional[Constraints] = Field(
        None,
        description='The following constraints are supported for `string` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type1(Enum):
    number = 'number'


class Format1(Enum):
    default = 'default'


class Constraints1(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[float]]] = None
    minimum: Optional[Union[str, float]] = None
    maximum: Optional[Union[str, float]] = None


class Fields1(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type1 = Field(
        ..., description='The type keyword, which `MUST` be a value of `number`.'
    )
    format: Optional[Format1] = Field(
        'default',
        description='There are no format keyword options for `number`: only `default` is allowed.',
    )
    bareNumber: Optional[bool] = Field(
        True,
        description='a boolean field with a default of `true`. If `true` the physical contents of this field must follow the formatting constraints already set out. If `false` the contents of this field may contain leading and/or trailing non-numeric characters (which implementors MUST therefore strip). The purpose of `bareNumber` is to allow publishers to publish numeric data that contains trailing characters such as percentages e.g. `95%` or leading characters such as currencies e.g. `€95` or `EUR 95`. Note that it is entirely up to implementors what, if anything, they do with stripped text.',
        title='bareNumber',
    )
    decimalChar: Optional[str] = Field(
        None,
        description='A string whose value is used to represent a decimal point within the number. The default value is `.`.',
    )
    groupChar: Optional[str] = Field(
        None,
        description="A string whose value is used to group digits within the number. The default value is `null`. A common value is `,` e.g. '100,000'.",
    )
    constraints: Optional[Constraints1] = Field(
        None,
        description='The following constraints are supported for `number` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type2(Enum):
    integer = 'integer'


class Constraints2(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[int]]] = None
    minimum: Optional[Union[str, int]] = None
    maximum: Optional[Union[str, int]] = None


class Fields2(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type2 = Field(
        ..., description='The type keyword, which `MUST` be a value of `integer`.'
    )
    format: Optional[Format1] = Field(
        'default',
        description='There are no format keyword options for `integer`: only `default` is allowed.',
    )
    bareNumber: Optional[bool] = Field(
        True,
        description='a boolean field with a default of `true`. If `true` the physical contents of this field must follow the formatting constraints already set out. If `false` the contents of this field may contain leading and/or trailing non-numeric characters (which implementors MUST therefore strip). The purpose of `bareNumber` is to allow publishers to publish numeric data that contains trailing characters such as percentages e.g. `95%` or leading characters such as currencies e.g. `€95` or `EUR 95`. Note that it is entirely up to implementors what, if anything, they do with stripped text.',
        title='bareNumber',
    )
    constraints: Optional[Constraints2] = Field(
        None,
        description='The following constraints are supported for `integer` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type3(Enum):
    date = 'date'


class Constraints3(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[List[str]] = Field(None, min_items=1, unique_items=True)
    minimum: Optional[str] = None
    maximum: Optional[str] = None


class Fields3(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type3 = Field(
        ..., description='The type keyword, which `MUST` be a value of `date`.'
    )
    format: Optional[Any] = Field(
        'default',
        description='The format keyword options for `date` are `default`, `any`, and `{PATTERN}`.',
    )
    constraints: Optional[Constraints3] = Field(
        None,
        description='The following constraints are supported for `date` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type4(Enum):
    time = 'time'


class Fields4(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type4 = Field(
        ..., description='The type keyword, which `MUST` be a value of `time`.'
    )
    format: Optional[Any] = Field(
        'default',
        description='The format keyword options for `time` are `default`, `any`, and `{PATTERN}`.',
    )
    constraints: Optional[Constraints3] = Field(
        None,
        description='The following constraints are supported for `time` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type5(Enum):
    datetime = 'datetime'


class Fields5(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type5 = Field(
        ..., description='The type keyword, which `MUST` be a value of `datetime`.'
    )
    format: Optional[Any] = Field(
        'default',
        description='The format keyword options for `datetime` are `default`, `any`, and `{PATTERN}`.',
    )
    constraints: Optional[Constraints3] = Field(
        None,
        description='The following constraints are supported for `datetime` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type6(Enum):
    year = 'year'


class Constraints6(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[int]]] = None
    minimum: Optional[Union[str, int]] = None
    maximum: Optional[Union[str, int]] = None


class Fields6(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type6 = Field(
        ..., description='The type keyword, which `MUST` be a value of `year`.'
    )
    format: Optional[Format1] = Field(
        'default',
        description='There are no format keyword options for `year`: only `default` is allowed.',
    )
    constraints: Optional[Constraints6] = Field(
        None,
        description='The following constraints are supported for `year` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type7(Enum):
    yearmonth = 'yearmonth'


class Constraints7(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[List[str]] = Field(None, min_items=1, unique_items=True)
    minimum: Optional[str] = None
    maximum: Optional[str] = None


class Fields7(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type7 = Field(
        ..., description='The type keyword, which `MUST` be a value of `yearmonth`.'
    )
    format: Optional[Format1] = Field(
        'default',
        description='There are no format keyword options for `yearmonth`: only `default` is allowed.',
    )
    constraints: Optional[Constraints7] = Field(
        None,
        description='The following constraints are supported for `yearmonth` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type8(Enum):
    boolean = 'boolean'


class Constraints8(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    enum: Optional[List[bool]] = Field(None, min_items=1, unique_items=True)


class Fields8(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type8 = Field(
        ..., description='The type keyword, which `MUST` be a value of `boolean`.'
    )
    format: Optional[Format1] = Field(
        'default',
        description='There are no format keyword options for `boolean`: only `default` is allowed.',
    )
    trueValues: Optional[List[str]] = Field(['true', 'True', 'TRUE', '1'], min_items=1)
    falseValues: Optional[List[str]] = Field(
        ['false', 'False', 'FALSE', '0'], min_items=1
    )
    constraints: Optional[Constraints8] = Field(
        None,
        description='The following constraints are supported for `boolean` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type9(Enum):
    object = 'object'


class Constraints9(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[Dict[str, Any]]]] = None
    minLength: Optional[int] = Field(
        None, description='An integer that specifies the minimum length of a value.'
    )
    maxLength: Optional[int] = Field(
        None, description='An integer that specifies the maximum length of a value.'
    )


class Fields9(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type9 = Field(
        ..., description='The type keyword, which `MUST` be a value of `object`.'
    )
    format: Optional[Format1] = Field(
        'default',
        description='There are no format keyword options for `object`: only `default` is allowed.',
    )
    constraints: Optional[Constraints9] = Field(
        None,
        description='The following constraints apply for `object` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type10(Enum):
    geopoint = 'geopoint'


class Format7(Enum):
    default = 'default'
    array = 'array'
    object = 'object'


class Constraints10(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[List], List[Dict[str, Any]]]] = None


class Fields10(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type10 = Field(
        ..., description='The type keyword, which `MUST` be a value of `geopoint`.'
    )
    format: Optional[Format7] = Field(
        'default',
        description='The format keyword options for `geopoint` are `default`,`array`, and `object`.',
    )
    constraints: Optional[Constraints10] = Field(
        None,
        description='The following constraints are supported for `geopoint` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type11(Enum):
    geojson = 'geojson'


class Format8(Enum):
    default = 'default'
    topojson = 'topojson'


class Constraints11(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[Dict[str, Any]]]] = None
    minLength: Optional[int] = Field(
        None, description='An integer that specifies the minimum length of a value.'
    )
    maxLength: Optional[int] = Field(
        None, description='An integer that specifies the maximum length of a value.'
    )


class Fields11(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type11 = Field(
        ..., description='The type keyword, which `MUST` be a value of `geojson`.'
    )
    format: Optional[Format8] = Field(
        'default',
        description='The format keyword options for `geojson` are `default` and `topojson`.',
    )
    constraints: Optional[Constraints11] = Field(
        None,
        description='The following constraints are supported for `geojson` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type12(Enum):
    array = 'array'


class Format9(Enum):
    default = 'default'


class Constraints12(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[Union[List[str], List[List]]] = None
    minLength: Optional[int] = Field(
        None, description='An integer that specifies the minimum length of a value.'
    )
    maxLength: Optional[int] = Field(
        None, description='An integer that specifies the maximum length of a value.'
    )


class Fields12(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type12 = Field(
        ..., description='The type keyword, which `MUST` be a value of `array`.'
    )
    format: Optional[Format9] = Field(
        'default',
        description='There are no format keyword options for `array`: only `default` is allowed.',
    )
    constraints: Optional[Constraints12] = Field(
        None,
        description='The following constraints apply for `array` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type13(Enum):
    duration = 'duration'


class Constraints13(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[List[str]] = Field(None, min_items=1, unique_items=True)
    minimum: Optional[str] = None
    maximum: Optional[str] = None


class Fields13(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type13 = Field(
        ..., description='The type keyword, which `MUST` be a value of `duration`.'
    )
    format: Optional[Format9] = Field(
        'default',
        description='There are no format keyword options for `duration`: only `default` is allowed.',
    )
    constraints: Optional[Constraints13] = Field(
        None,
        description='The following constraints are supported for `duration` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Type14(Enum):
    any = 'any'


class Constraints14(BaseModel):
    required: Optional[bool] = Field(
        None,
        description='Indicates whether a property must have a value for each instance.',
    )
    unique: Optional[bool] = Field(
        None, description='When `true`, each value for the property `MUST` be unique.'
    )
    enum: Optional[List] = Field(None, min_items=1, unique_items=True)


class Fields14(BaseModel):
    name: str = Field(..., description='A name for this field.', title='Name')
    title: Optional[str] = Field(
        None,
        description='A human-readable title.',
        examples=['{\n  "title": "My Package Title"\n}\n'],
        title='Title',
    )
    description: Optional[str] = Field(
        None,
        description='A text description. Markdown is encouraged.',
        examples=[
            '{\n  "description": "# My Package description\\nAll about my package."\n}\n'
        ],
        title='Description',
    )
    example: Optional[str] = Field(
        None,
        description='An example value for the field.',
        examples=['{\n  "example": "Put here an example value for your field"\n}\n'],
        title='Example',
    )
    type: Type14 = Field(
        ..., description='The type keyword, which `MUST` be a value of `any`.'
    )
    constraints: Optional[Constraints14] = Field(
        None,
        description='The following constraints apply to `any` fields.',
        title='Constraints',
    )
    rdfType: Optional[str] = Field(None, description='The RDF type for this field.')


class Reference(BaseModel):
    resource: str
    fields: List[str] = Field(..., min_items=1, unique_items=True)


class ForeignKeys(BaseModel):
    fields: List[constr(min_items=1)]
    reference: Reference


class Reference1(BaseModel):
    resource: str
    fields: str


class ForeignKeys1(BaseModel):
    fields: str = Field(..., description='Fields that make up the primary key.')
    reference: Reference1


class TableSchema(BaseModel):
    fields: List[
        Union[
            Fields,
            Fields1,
            Fields2,
            Fields3,
            Fields4,
            Fields5,
            Fields6,
            Fields7,
            Fields8,
            Fields9,
            Fields10,
            Fields11,
            Fields12,
            Fields13,
            Fields14,
        ]
    ] = Field(
        ...,
        description='An `array` of Table Schema Field objects.',
        examples=[
            '{\n  "fields": [\n    {\n      "name": "my-field-name"\n    }\n  ]\n}\n',
            '{\n  "fields": [\n    {\n      "name": "my-field-name",\n      "type": "number"\n    },\n    {\n      "name": "my-field-name-2",\n      "type": "string",\n      "format": "email"\n    }\n  ]\n}\n',
        ],
        min_items=1,
    )
    primaryKey: Optional[Union[List[str], str]] = Field(
        None,
        description='A primary key is a field name or an array of field names, whose values `MUST` uniquely identify each row in the table.',
        examples=[
            '{\n  "primaryKey": [\n    "name"\n  ]\n}\n',
            '{\n  "primaryKey": [\n    "first_name",\n    "last_name"\n  ]\n}\n',
        ],
    )
    foreignKeys: Optional[List[Union[ForeignKeys, ForeignKeys1]]] = Field(
        None,
        examples=[
            '{\n  "foreignKeys": [\n    {\n      "fields": "state",\n      "reference": {\n        "resource": "the-resource",\n        "fields": "state_id"\n      }\n    }\n  ]\n}\n',
            '{\n  "foreignKeys": [\n    {\n      "fields": "state",\n      "reference": {\n        "resource": "",\n        "fields": "id"\n      }\n    }\n  ]\n}\n',
        ],
        min_items=1,
    )
    missingValues: Optional[List[str]] = Field(
        [''],
        description="Values that when encountered in the source, should be considered as `null`, 'not present', or 'blank' values.",
        examples=[
            '{\n  "missingValues": [\n    "-",\n    "NaN",\n    ""\n  ]\n}\n',
            '{\n  "missingValues": []\n}\n',
        ],
    )
