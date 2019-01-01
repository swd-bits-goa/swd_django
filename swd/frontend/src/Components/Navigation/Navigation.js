
/* eslint no-unused-vars:0 */
import React from 'react';
import PropTypes from 'prop-types';
import {withRouter} from 'react-router';
import AppBar from 'material-ui/AppBar';
import IconButton from 'material-ui/IconButton';
import FlatButton from 'material-ui/FlatButton';
import NavigationMenu from 'material-ui/svg-icons/navigation/menu';
import { Toolbar, ToolbarGroup, ToolbarSeparator, ToolbarTitle } from 'material-ui/Toolbar';
import NavigationExpandMoreIcon from 'material-ui/svg-icons/navigation/expand-more';
import MenuItem from 'material-ui/MenuItem';
import IconMenu from 'material-ui/IconMenu';
import RaisedButton from 'material-ui/RaisedButton';
import ActionSearch from 'material-ui/svg-icons/action/search';
import Avatar from 'material-ui/Avatar';
import {withApollo} from 'react-apollo';
import { grey200, grey50 } from 'material-ui/styles/colors';
import Sidebar from '../Sidebar/Sidebar.js';
// Import custom navigation styles
import s from './Navigation.css';
import logoUrl from './logo-small.png';
import LoginModal from './LoginModal';
import { Mobile } from '../Responsive';
import { Tablet } from '../Responsive';
import Search from '../Search/Search.js';
import SearchBarWithAnimation from '../Search/SearchBar.js';
import {Link, BrowserRouter, Route} from 'react-router-dom';
import Layout from "../Layout/Layout";
import backIcon from './back.svg';
import {cyan500, cyan900, white} from "material-ui/styles/colors";

class Navigation extends React.Component {
  static propTypes = {
    isLoggedIn: PropTypes.bool.isRequired,
    logout: PropTypes.func.isRequired,
    searchMode: PropTypes.bool.isRequired
  };

constructor(props) {
  super(props);
  this.state = {
    sidebarOpen: false,
    searchMode: props.searchMode
  };
  this.handleSideBarToggle = this.handleSideBarToggle.bind(this);
}

  handleSideBarToggle = () => {
    this.setState( prevState => ({
  sidebarOpen: !prevState.sidebarOpen
}));
}

  handleCloseSearch = () => {
    this.setState({ search: false });
    // Closing search returns to home for now
    this.props.history.push("/");
  }

  goToLogin = () => {
    this.props.history.push("/login");
  };

  handleLogout = () => {
    localStorage.removeItem('token')
    this.props.logout()
    this.props.client.resetStore()
  }

  render() {
    const filledIcon = {
      width: 24,
      height: 24,
    };
      const toolbarStyle = {
          backgroundColor: cyan500,
      }
      const appBarColor = {
          color: white
      }
    return (

      // There's a noticeable lag when rendering components based on
      // media queries for the first time
      <Mobile>
      <div>
        <div className={s.AppBar}>
          <Toolbar style={toolbarStyle}>
            <ToolbarGroup firstChild>
                {!this.state.searchMode?
                    <IconButton onClick={this.handleSideBarToggle}><NavigationMenu color={white} /></IconButton>
                    :<IconButton onClick={this.handleCloseSearch} ><img src={backIcon} height={25}/></IconButton>}

              <Sidebar open={this.state.sidebarOpen} toggleOpen={this.handleSideBarToggle} />
                {this.state.searchMode?<SearchBarWithAnimation style={{width: '80%'}}/>:<Link to='/' style={{textDecoration : "none"}}><ToolbarTitle style={appBarColor} text="SWD" /></Link>}

            </ToolbarGroup>
            <ToolbarGroup lastChild style={{position: 'relative'}}>
              {this.state.searchMode?<span/>:<Link to='/search/' style={{position: 'absolute', left: 5}}><IconButton iconStyle={filledIcon} style={{paddingLeft: 0, paddingRight: 20}} onClick={this.handleSearch}><ActionSearch color={"#fff"} /></IconButton></Link>}
              {this.state.searchMode?<span/>:<ToolbarSeparator style={{position: 'absolute', left: 20}}/>}
              {!this.state.searchMode? !(this.props.isLoggedIn) ?
              <FlatButton label="Login" onTouchTap={this.goToLogin}  style={{left: 20, color: cyan900}}/>
              :
             <FlatButton label="Logout" onTouchTap={this.handleLogout}  style={{left: 20, color: cyan900}}/>
              :<span/>}

            </ToolbarGroup>

          </Toolbar>
        </div>
      </div>
      </Mobile>
    );

  }
}

export default withRouter(withApollo(Navigation));
