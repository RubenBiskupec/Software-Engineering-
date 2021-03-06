import React, { Component } from 'react';
import Autosuggest from 'react-autosuggest';
import PropTypes from 'prop-types';
import Absolute from '../Absolute';

const escapeRegexCharacters = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const getSuggestions = (value, products) => {
  const escapedValue = escapeRegexCharacters(value.trim());

  if (escapedValue === '') {
    return [];
  }

  const regex = new RegExp(`^${escapedValue}`, 'i');

  return products.filter((product) => regex.test(product.name));
};

const getSuggestionValue = (suggestion) => suggestion.name;

const renderSuggestion = (suggestion) => <span>{suggestion.name}</span>;

/**
 * Decides whether to show suggestions or not.
 * Returns true only if the input size is larger than 2.
 * @param value the input of the user
 * @returns {boolean} whether to show the suggestions
 */
function shouldRenderSuggestions(value) {
  return value.trim().length > 2;
}

const ProductAutosuggest = class extends Component {
  constructor(props) {
    super(props);
    this.state = {
      suggestions: [],
      products: [],
    };
    this.handleTextChange = this.handleTextChange.bind(this);
    this.onSuggestionSelectedByUser = this.onSuggestionSelectedByUser.bind(
      this,
    );
    this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(
      this,
    );
    this.onSuggestionsClearRequested = this.onSuggestionsClearRequested.bind(
      this,
    );
  }

  componentDidMount() {
    this.fillProductsArray();
  }

  onSuggestionsFetchRequested({ value }) {
    const { products } = this.state;
    this.setState({
      suggestions: getSuggestions(value, products),
    });
  }

  onSuggestionsClearRequested() {
    this.setState({
      suggestions: [],
    });
  }

  onSuggestionSelectedByUser(event, { suggestionValue }) {
    const { onTextChangeAuto } = this.props;
    onTextChangeAuto(suggestionValue);
  }

  async fillProductsArray() {
    const absolute = this.context;
    const products = [];
    const url = `${
      absolute ? 'https://retaily.site:7000' : ''
    }/inventaris/tabel`;
    await fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then(
        (response) => {
          Object.keys(response).forEach((product) => {
            products.push(response[product]);
          });
          this.setState({ products });
        },
        (error) => {
          console.log(error);
        },
      );
  }

  handleTextChange(event) {
    const { onTextChange } = this.props;
    onTextChange(event);
  }

  render() {
    const { text } = this.props;
    const { suggestions } = this.state;
    const inputProps = {
      placeholder: 'Naam van product',
      value: text,
      onChange: this.handleTextChange,
    };
    return (
      <Autosuggest
        suggestions={suggestions}
        onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
        onSuggestionsClearRequested={this.onSuggestionsClearRequested}
        getSuggestionValue={getSuggestionValue}
        renderSuggestion={renderSuggestion}
        shouldRenderSuggestions={shouldRenderSuggestions}
        onSuggestionSelected={this.onSuggestionSelectedByUser}
        inputProps={inputProps}
      />
    );
  }
};

ProductAutosuggest.propTypes = {
  text: PropTypes.string.isRequired,
  onTextChangeAuto: PropTypes.func.isRequired,
  onTextChange: PropTypes.func.isRequired,
};

ProductAutosuggest.contextType = Absolute;

export default ProductAutosuggest;
