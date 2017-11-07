
import React from 'react';
import PropTypes from 'prop-types';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import withStyles from 'isomorphic-style-loader/lib/withStyles';
import s from './Layout.css';
import Header from '../Header';
import Footer from '../Footer';
import Sidebar from '../Sidebar';


class Layout extends React.Component {
  static propTypes = {
    children: PropTypes.node.isRequired,
    isLoggedIn: PropTypes.bool.isRequired,
  };

  state = {
    sideBarOpen: true,
  };

  handleSideBarToggle = () => {
    this.setState({ sideBarOpen: !this.state.sideBarOpen });
  };

  render() {
    const contentBodyStyle = { transition: 'margin-left 450ms cubic-bezier(0.23, 1, 0.32, 1)' };

    if (this.state.sideBarOpen && this.props.isLoggedIn) {
      contentBodyStyle.marginLeft = 256;
    } else {
      contentBodyStyle.marginLeft = 0;
    }

    return (
      <MuiThemeProvider muiTheme={this.context.muiTheme}>
        <div>
          <div style={contentBodyStyle}>
            <Header
              toggleFunc={this.handleSideBarToggle}
              sideBarOpen={this.state.sideBarOpen}
              isLoggedIn={this.props.isLoggedIn}
            />
            {this.props.children}
            <Footer
              isLoggedIn={this.props.isLoggedIn}
            />
          </div>

          { this.props.isLoggedIn ? (
            <Sidebar
              open={this.state.sideBarOpen}
            />
        ) : null }

        </div>
      </MuiThemeProvider>
    );
  }
}

Layout.contextTypes = {
  muiTheme: PropTypes.object.isRequired,
};

export default withStyles(s)(Layout);
