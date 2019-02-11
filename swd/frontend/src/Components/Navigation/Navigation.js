
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
import Menu from 'material-ui/Menu';
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
import { Mobile, Tablet } from '../Responsive';
import Search from '../Search/Search.js';
import SearchBarWithAnimation from '../Search/SearchBar.js';
import {Link, BrowserRouter, Route} from 'react-router-dom';
import Layout from "../Layout/Layout";
import backIcon from './back.svg';
import bits from './bits.svg';
import swd from './swd.svg';
import line from './line.svg';
import {cyan500, cyan900, white} from "material-ui/styles/colors";
import { darkBlack } from 'material-ui/styles/colors';

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
          backgroundColor: white,
          height: 91,
      }
      const appBarColor = {
          color: darkBlack
      }
    return (

      // There's a noticeable lag when rendering components based on
      // media queries for the first time
      <div className={s.mainDiv}>
        <Mobile>
          <div>
            <div className={s.AppBar}>
              <Toolbar style={toolbarStyle}>
                <ToolbarGroup firstChild>
                    {!this.state.searchMode?
                        <IconButton onClick={this.handleSideBarToggle}><NavigationMenu color={"#074F57"} height={44}/></IconButton>
                        :<IconButton onClick={this.handleCloseSearch} ><img src={backIcon} height={25}/></IconButton>}

                  <Sidebar open={this.state.sidebarOpen} toggleOpen={this.handleSideBarToggle} isLoggedIn={this.props.isLoggedIn}/>
                    {this.state.searchMode?<SearchBarWithAnimation style={{width: '80%'}}/>:<Link to='/' style={{textDecoration : "none"}}><img src={bits} height={44} alt="BITS Pilani Goa Campus"/> <img src={line} height={44} alt="divider" /> <img src={swd} height={44} alt="Student Welfare Division"/></Link>}

                </ToolbarGroup>
                <ToolbarGroup lastChild style={{position: 'relative'}}>
                  {this.state.searchMode?<span/>:<Link to='/search/' style={{position: 'absolute', left: 5}}><IconButton iconStyle={filledIcon} style={{paddingLeft: 0, paddingRight: 20}} onClick={this.handleSearch}><ActionSearch color={"#000"} /></IconButton></Link>}
                  {this.state.searchMode?<span/>:<ToolbarSeparator style={{position: 'absolute', left: 20}}/>}
                
                </ToolbarGroup>
                
              </Toolbar>
            </div>
          </div>
        </Mobile>
        <Tablet>
          <div className={s.AppBarDespktop}>
          <Toolbar style={toolbarStyle}>
                <ToolbarGroup firstChild>
                  <Link to='/' style={{textDecoration : "none"}}>
                    <img src={bits} height={44} alt="BITS Pilani Goa Campus"/>
                    <img src={line} height={50} alt="divider" />
                    <img src={swd} height={50} alt="Student Welfare Division"/></Link>

                </ToolbarGroup>
                <ToolbarGroup>

                </ToolbarGroup>
              </Toolbar>   
          </div> 
        </Tablet>
      
      </div>
     
    );

  }
}

export default withRouter(withApollo(Navigation));
