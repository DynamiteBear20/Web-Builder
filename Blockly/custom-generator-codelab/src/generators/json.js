import * as Blockly from 'blockly';

export const htmlGenerator = new Blockly.Generator('HTML');
const Order = {
    ATOMIC: 0,
  };

htmlGenerator.forBlock['head'] = function(block, generator) {
  const code = generator.statementToCode(block,'CONTENT');
  const headCode = '<head>\n'+code+'\n</head>\n';
  return [headCode,Order.ATOMIC];
};
htmlGenerator.forBlock['body'] = function(block, generator) {
  const bodyCode = `<body>\n${generator.statementToCode(block,'CONTENT')}\n</body>\n`;
  return [bodyCode,Order.ATOMIC];
};
htmlGenerator.forBlock['logic_null'] = function(block) {
    return ['null', Order.ATOMIC];
};
/*jsonGenerator.forBlock['text'] = function(block) {
    const textValue = block.getFieldValue('TEXT');
    const code = `"${textValue}"`;
    return [code, Order.ATOMIC];
  };
jsonGenerator.forBlock['math_number'] = function(block) {
    const code = String(block.getFieldValue('NUM'));
    return [code, Order.ATOMIC];
  };
jsonGenerator.forBlock['logic_boolean'] = function(block) {
    const code = (block.getFieldValue('BOOL') === 'TRUE') ? 'true' : 'false';
    return [code, Order.ATOMIC];
  };
jsonGenerator.forBlock['member'] = function(block, generator) {
    const name = block.getFieldValue('MEMBER_NAME');
    const value = generator.valueToCode(
        block, 'MEMBER_VALUE', Order.ATOMIC);
    const code = `"${name}": ${value}`;
    return code;
  };
  jsonGenerator.forBlock['lists_create_with'] = function(block, generator) {
    const values = [];
    for (let i = 0; i < block.itemCount_; i++) {
      const valueCode = generator.valueToCode(block, 'ADD' + i,
          Order.ATOMIC);
      if (valueCode) {
        values.push(valueCode);
      }
    }
    const valueString = values.join(',\n');
    const indentedValueString =
        generator.prefixLines(valueString, generator.INDENT);
    const codeString = '[\n' + indentedValueString + '\n]';
    return [codeString, Order.ATOMIC];
  };
  jsonGenerator.forBlock['object'] = function(block, generator) {
    const statementMembers =
        generator.statementToCode(block, 'MEMBERS');
    const code = '{\n' + statementMembers + '\n}';
    return [code, Order.ATOMIC];
  };*/
  htmlGenerator.scrub_ = function(block, code, thisOnly) {
    const nextBlock =
        block.nextConnection && block.nextConnection.targetBlock();
    if (nextBlock && !thisOnly) {
      return code + ',\n' + htmlGenerator.blockToCode(nextBlock);
    }
    return code;
  };