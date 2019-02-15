
import React from 'react';
import PropTypes from 'prop-types';

import s from './Layout.css';
import Header from '../Header';
import Footer from '../Footer';
import Sidebar from '../Sidebar';



class Layout extends React.Component {
  static propTypes = {
    children: PropTypes.node.isRequired,
    isLoggedIn: PropTypes.bool.isRequired,
    logout: PropTypes.func.isRequired,
    searchMode: PropTypes.bool.isRequired,
  };


  render() {
    return (

        <div className={s.container}>
          <div>
          
            <Header
              isLoggedIn={this.props.isLoggedIn}
              logout={this.props.logout}
              searchMode={this.props.searchMode}
              />
            {this.props.children}
            <Footer
              isLoggedIn={this.props.isLoggedIn}/>
          </div>

        </div>
    );
  }
}

export default (Layout);
