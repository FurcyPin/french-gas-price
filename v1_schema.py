v1_schema = """
{
  "fields": [
    {
      "metadata": {},
      "name": "_cp",
      "nullable": true,
      "type": "string"
    },
    {
      "metadata": {},
      "name": "_id",
      "nullable": true,
      "type": "long"
    },
    {
      "metadata": {},
      "name": "_latitude",
      "nullable": true,
      "type": "double"
    },
    {
      "metadata": {},
      "name": "_longitude",
      "nullable": true,
      "type": "double"
    },
    {
      "metadata": {},
      "name": "_pop",
      "nullable": true,
      "type": "string"
    },
    {
      "metadata": {},
      "name": "adresse",
      "nullable": true,
      "type": "string"
    },
    {
      "metadata": {},
      "name": "horaires",
      "nullable": true,
      "type": {
        "fields": [
          {
            "metadata": {},
            "name": "_automate-24-24",
            "nullable": true,
            "type": "string"
          },
          {
            "metadata": {},
            "name": "jour",
            "nullable": true,
            "type": {
              "containsNull": true,
              "elementType": {
                "fields": [
                  {
                    "metadata": {},
                    "name": "_VALUE",
                    "nullable": true,
                    "type": "string"
                  },
                  {
                    "metadata": {},
                    "name": "_ferme",
                    "nullable": true,
                    "type": "string"
                  },
                  {
                    "metadata": {},
                    "name": "_id",
                    "nullable": true,
                    "type": "long"
                  },
                  {
                    "metadata": {},
                    "name": "_nom",
                    "nullable": true,
                    "type": "string"
                  },
                  {
                    "metadata": {},
                    "name": "horaire",
                    "nullable": true,
                    "type": {
                      "containsNull": true,
                      "elementType": {
                        "fields": [
                          {
                            "metadata": {},
                            "name": "_VALUE",
                            "nullable": true,
                            "type": "string"
                          },
                          {
                            "metadata": {},
                            "name": "_fermeture",
                            "nullable": true,
                            "type": "double"
                          },
                          {
                            "metadata": {},
                            "name": "_ouverture",
                            "nullable": true,
                            "type": "double"
                          }
                        ],
                        "type": "struct"
                      },
                      "type": "array"
                    }
                  }
                ],
                "type": "struct"
              },
              "type": "array"
            }
          }
        ],
        "type": "struct"
      }
    },
    {
      "metadata": {},
      "name": "prix",
      "nullable": true,
      "type": {
        "containsNull": true,
        "elementType": {
          "fields": [
            {
              "metadata": {},
              "name": "_VALUE",
              "nullable": true,
              "type": "string"
            },
            {
              "metadata": {},
              "name": "_id",
              "nullable": true,
              "type": "long"
            },
            {
              "metadata": {},
              "name": "_maj",
              "nullable": true,
              "type": "timestamp"
            },
            {
              "metadata": {},
              "name": "_nom",
              "nullable": true,
              "type": "string"
            },
            {
              "metadata": {},
              "name": "_valeur",
              "nullable": true,
              "type": "double"
            }
          ],
          "type": "struct"
        },
        "type": "array"
      }
    },
    {
        "metadata": {},
        "name": "rupture",
        "nullable": true,
        "type": {
            "containsNull": true,
            "elementType": {
                "fields": [
                    {
                        "metadata": {},
                        "name": "_VALUE",
                        "nullable": true,
                        "type": "string"
                    },
                    {
                        "metadata": {},
                        "name": "_debut",
                        "nullable": true,
                        "type": "timestamp"
                    },
                    {
                        "metadata": {},
                        "name": "_fin",
                        "nullable": true,
                        "type": "string"
                    },
                    {
                        "metadata": {},
                        "name": "_id",
                        "nullable": true,
                        "type": "long"
                    },
                    {
                        "metadata": {},
                        "name": "_nom",
                        "nullable": true,
                        "type": "string"
                    },
                    {
                        "metadata": {},
                        "name": "_type",
                        "nullable": true,
                        "type": "string"
                    }
                ],
                "type": "struct"
            },
            "type": "array"
        }
    },
    {
      "metadata": {},
      "name": "services",
      "nullable": true,
      "type": {
        "fields": [
          {
            "metadata": {},
            "name": "service",
            "nullable": true,
            "type": {
              "containsNull": true,
              "elementType": "string",
              "type": "array"
            }
          }
        ],
        "type": "struct"
      }
    },
    {
      "metadata": {},
      "name": "ville",
      "nullable": true,
      "type": "string"
    }
  ],
  "type": "struct"
}
"""