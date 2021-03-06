/*
  Copyright (C) 2018 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

const MAX_COLUMNS_COUNT = 1000;

export default can.Map({
  define: {
    isValidConfiguration: {
      get() {
        let isSelected = (item) => item.attr('isSelected');

        let selectedAttributesCount =
          this.attr('attributes').filter(isSelected).length +
          this.attr('localAttributes').filter(isSelected).length +
          this.attr('mappings').filter(isSelected).length;

        return selectedAttributesCount <= this.attr('maxAttributesCount');
      },
    },
    useLocalAttribute: {
      get() {
        return this.attr('type') === 'Assessment';
      },
    },
  },
  type: 'Program',
  filter: '',
  maxAttributesCount: MAX_COLUMNS_COUNT,
  relevant: can.compute(() => {
    return new can.List();
  }),
  attributes: new can.List(),
  localAttributes: new can.List(),
  mappings: new can.List(),
  init() {
    this.setAttributes();
  },
  setAttributes() {
    let type = this.attr('type');

    let definitions = this.getModelAttributeDefenitions(type);
    let filtered = _.filter(definitions, (def) => {
      return this.filterModelAttributes(def);
    });

    let attributes = _.filter(filtered, (el) => {
      return el.type !== 'mapping' && el.type !== 'object_custom';
    });

    let mappings = _.filter(filtered, (el) => {
      return el.type === 'mapping';
    });

    this.attr('attributes', attributes);
    this.attr('mappings', mappings);

    let localAttributes = [];
    if (this.attr('useLocalAttribute')) {
      localAttributes = _.filter(filtered, (el) => {
        return el.type === 'object_custom';
      });
    }
    this.attr('localAttributes', localAttributes);
  },
  changeType(type) {
    this.attr('relevant', []);
    this.attr('filter', '');
    this.attr('snapshot_type', '');
    this.attr('has_parent', false);
    this.attr('type', type);

    if (this.attr('type') === 'Snapshot') {
      this.attr('snapshot_type', 'Control');
    }

    this.setAttributes();
  },
  getModelAttributeDefenitions(type) {
    return GGRC.model_attr_defs ? GGRC.model_attr_defs[type] : [];
  },
  filterModelAttributes(attr) {
    return !attr.import_only &&
      attr.display_name.indexOf('unmap:') === -1;
  },
});
