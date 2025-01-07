/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import * as Blockly from 'blockly/core';

// Create a custom block called 'add_text' that adds
// text to the output div on the sample app.
// This is just an example and you should replace this with your
// own custom blocks.
export const blocks = Blockly.common.createBlockDefinitionsFromJsonArray([{
  "type": "head",
  "message0": "<head>%1 %2</head>",
  "args0": [
    {
      "type": "input_dummy"
    },
    {
      "type": "input_statement",
      "name": "CONTENT"
    }
  ],
  "colour": 230,
  "previousStatement":null,
  "nextStatement":null,
},{
"type": "body",
  "message0": "<body>%1 %2</body>",
  "args0": [
    {
      "type": "input_dummy"
    },
    {
      "type": "input_statement",
      "name": "CONTENT"
    }
  ],
  "colour": 230,
  "previousStatement":null,
  "nextStatement":null,
}]);
