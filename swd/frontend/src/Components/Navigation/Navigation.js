
/* eslint no-unused-vars:0 */
import React from 'react';
import PropTypes from 'prop-types';
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
import Search from '../Search/Search.js';
import SearchBar from '../Search/SearchBar.js';
import {Link, BrowserRouter, Route} from 'react-router-dom';
import Layout from "../Layout/Layout";
import closeIcon from './close.svg';

class Navigation extends React.Component {
  static propTypes = {
    isLoggedIn: PropTypes.bool.isRequired,
    login: PropTypes.func.isRequired,
    logout: PropTypes.func.isRequired,
    setPutSearch: PropTypes.func.isRequired,
    search: PropTypes.bool.isRequired
  };

constructor(props) {
  super(props);
  this.state = {
    loginModalOpen : false,
    sidebarOpen: false,
    open: false,
    search: props.search,
    putSearch: " "
  };
  this.handleSideBarToggle = this.handleSideBarToggle.bind(this);
  this.getSearch = this.getSearch.bind(this);
}

  handleSideBarToggle = () => {
    this.setState( prevState => ({
  sidebarOpen: !prevState.sidebarOpen
}));
}
    
  componentWillMount(){
    window.location.pathname==='/Search'?this.setState({search: true}):this.setState({search: false});
  }
  
  getSearch = (e) => {
    this.setState({putSearch: e});
    this.props.setPutSearch(e);
  }

  handleSideClick = () => {
    this.setState({ sideBarOpen: !this.state.sideBarOpen});
  }

  /*handleSearch = () => {
    this.setState({ search: true });
  }*/

  handleCloseSearch = () => {
    this.setState({ search: false });
  }

  handleLoginOpen = () => {
    this.setState({ loginModalOpen: true });
  };

  handleLoginClose = () => {
    this.setState({ loginModalOpen: false });
  };

  handleLogout = () => {
    localStorage.removeItem('token')
    this.props.logout()
    this.props.client.resetStore()
  }

  render() {
    const darkGreen = '#0B2326';
    const filledIcon = {
      width: 24,
      height: 24,
    };
    
    return (

      // There's a noticeable lag when rendering components based on
      // media queries for the first time
      <Mobile>
      <BrowserRouter>
      <div>
        <div className={s.AppBar}>
          <Toolbar>
            <ToolbarGroup firstChild>
              <IconButton onClick={this.handleSideBarToggle}><NavigationMenu color={darkGreen} /></IconButton>
              <Sidebar open={this.state.sidebarOpen} toggleOpen={this.handleSideBarToggle} />
              {this.state.search?<SearchBar style={{width: '90%'}} getSearch={this.getSearch}/>:<ToolbarTitle text="SWD" />}
              {this.state.search?<span/>:<ToolbarSeparator style={{marginLeft:0}} />}
            </ToolbarGroup>
            <ToolbarGroup lastChild style={{position: 'relative'}}>
              {this.state.search?<span/>:<Link to='/Search' style={{position: 'absolute', left: 5}}><IconButton iconStyle={filledIcon} style={{paddingLeft: 0, paddingRight: 20}} onClick={this.handleSearch}><ActionSearch color={darkGreen} /></IconButton></Link>}
              {this.state.search?<span/>:<ToolbarSeparator style={{position: 'absolute', left: 20}}/>}
              {!this.state.search? !(this.props.isLoggedIn) ? 
              <FlatButton label="Login" onTouchTap={this.handleLoginOpen}  style={{paddingLeft: 20}}/>
              :
             <FlatButton label="Logout" onTouchTap={this.handleLogout}  style={{paddingLeft: 20}}/>
              :<FlatButton onClick={this.handleCloseSearch} style={{position: 'relative', left: 20}}><img src={closeIcon} style={{position: 'relative', left: 5, height: 20}}/></FlatButton>}

            </ToolbarGroup>
            
          </Toolbar>
          <LoginModal
            open={this.state.loginModalOpen}
            onRequestClose={this.handleLoginClose}
            login={this.props.login} />
        </div>
      </div>
      </BrowserRouter>
      </Mobile>
    );

  }
}

export default withApollo(Navigation);
