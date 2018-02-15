
import React from 'react';
import PropTypes from 'prop-types';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';
import s from './Layout.css';
import Header from '../Header';
import Footer from '../Footer';
import Sidebar from '../Sidebar';

//Sets the material-ui theme colors and settings
const muiTheme = getMuiTheme({userAgent: navigator.userAgent});

class Layout extends React.Component {
  static propTypes = {
    children: PropTypes.node.isRequired,
    isLoggedIn: PropTypes.bool.isRequired,
    login: PropTypes.func.isRequired,
    logout: PropTypes.func.isRequired
  };


  render() {

    return (
      <MuiThemeProvider muiTheme={muiTheme}>
        <div className={s.container}>
          <div>
            <Header
              isLoggedIn={this.props.isLoggedIn}
              login={this.props.login}
              logout={this.props.logout}
            />
            {this.props.children}
            <Footer
              isLoggedIn={this.props.isLoggedIn}
            />
          </div>

        </div>
      </MuiThemeProvider>
    );
  }
}

export default (Layout);
