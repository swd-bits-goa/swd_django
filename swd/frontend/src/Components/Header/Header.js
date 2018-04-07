
import React from 'react';
import PropTypes from 'prop-types';
import s from './Header.css';
import Navigation from '../Navigation';

class Header extends React.Component {

  static propTypes = {
    isLoggedIn: PropTypes.bool.isRequired,
    logout: PropTypes.func.isRequired,
    searchMode:PropTypes.bool.isRequired
  };

  render() {
    return (
      <div className={s.root}>
        <Navigation
          isLoggedIn={this.props.isLoggedIn}
          logout={this.props.logout}
          searchMode={this.props.searchMode}/>
      </div>
    );
  }
}

export default (Header);
