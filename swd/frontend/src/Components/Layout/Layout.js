
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

  state = {
    sideBarOpen: false,
  };

  handleSideBarToggle = () => {
    this.setState({ sideBarOpen: !this.state.sideBarOpen });
  };

  render() {
    const contentBodyStyle = { transition: 'margin-left 450ms cubic-bezier(0.23, 1, 0.32, 1)' };

    if (this.state.sideBarOpen) {
      contentBodyStyle.marginLeft = 256;
    } else {
      contentBodyStyle.marginLeft = 0;
    }

    return (
      <MuiThemeProvider muiTheme={muiTheme}>
        <div className={s.container}>
          <div style={contentBodyStyle}>
            <Header
              toggleSideBar={this.handleSideBarToggle}
              sideBarOpen={this.state.sideBarOpen}
              isLoggedIn={this.props.isLoggedIn}
              login={this.props.login}
              logout={this.props.logout}
            />
            {this.props.children}
            <Footer
              isLoggedIn={this.props.isLoggedIn}
            />
          </div>

            <Sidebar
              open={this.state.sideBarOpen}
              toggleOpen={this.handleSideBarToggle}
            />

        </div>
      </MuiThemeProvider>
    );
  }
}

export default (Layout);
