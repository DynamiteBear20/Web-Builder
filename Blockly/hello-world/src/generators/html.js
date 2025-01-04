import * as Blockly from 'blockly';

export const jsonGenerator = new Blockly.Generator('HTML');
const Order = {
    ATOMIC: 0,
  };
jsonGenerator.forBlock['body'] = function(block,generator) {
    const statementMembers =
        generator.statementToCode(block, 'STATEMENTS');
    const attributes = generator.getFieldValue('ATTRIBUTES');
    
};