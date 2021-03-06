/*
    Copyright (C) 2018 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

/*
DO NOT EDIT - this is an auto generated file.

The file was generated by peg.js from src/parser/parsec.pegjs
see: src/parser/generate_parser.js

*/

export default {
  parse(query) {
    try {
      return this.generated.parse(query);
    } catch (e) {
      // force text search if anything goes wrong
      return this.generated.parse("~" + query);
    }
  },
  joinQueries(left, right, op = 'AND') {
    if (!left.expression.op){
      return right;
    }
    if (!right.expression.op){
      return left;
    }
    let expression = {
      left: left.expression,
      op: {name: op},
      right: right.expression,
    }
    return {
      expression,
    }
  },
  generated: "GENERATED_PLACEHOLDER"
};
