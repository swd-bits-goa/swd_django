
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
// Import custom navigation styles
import s from './Navigation.css';
import logoUrl from './logo-small.png';
import LoginModal from './LoginModal';
import { Mobile } from '../Responsive';

class Navigation extends React.Component {
  static propTypes = {
    isLoggedIn: PropTypes.bool.isRequired,
    toggleSideBar: PropTypes.func.isRequired,
    sideBarOpen: PropTypes.bool.isRequired,
    login: PropTypes.func.isRequired,
    logout: PropTypes.func.isRequired
  };

constructor(props) {
  super(props);
  this.state = {
    loginModalOpen : false,
  };
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
        <div className={s.AppBar}>
          <Toolbar>
            <ToolbarGroup firstChild>
              <IconButton onTouchTap={this.props.toggleSideBar}><NavigationMenu color={darkGreen} /></IconButton>
              <ToolbarTitle text="SWD" />
              <ToolbarSeparator />
            </ToolbarGroup>
            <ToolbarGroup lastChild>
              <IconButton iconStyle={filledIcon}><ActionSearch color={darkGreen} /></IconButton>
              { !(this.props.isLoggedIn) ? 
              <RaisedButton label="Login" backgroundColor={darkGreen} labelColor={grey50} onTouchTap={this.handleLoginOpen} />
              :
             <RaisedButton label="Logout" backgroundColor={darkGreen} labelColor={grey50} onTouchTap={this.handleLogout} />
              }

            </ToolbarGroup>
            
          </Toolbar>
          <LoginModal
            open={this.state.loginModalOpen}
            onRequestClose={this.handleLoginClose}
            login={this.props.login} />
        </div>
      </Mobile>
    );

    // if (!this.props.isLoggedIn) {
    //   return (
    //     <div>
    //       <Toolbar>
    //         <ToolbarGroup>
    //           <a href="/">
    //             <img
    //               src={logoUrl}
    //               width="50"
    //               height="50"
    //               style={{ padding: 20 }}
    //               alt="SWD"
    //             />
    //           </a>
    //           <ToolbarTitle text="SWD" href="/" />
    //         </ToolbarGroup>
    //         <ToolbarGroup>
    //           <IconButton tooltip="Search Students" href="/search">
    //             <ActionSearch />
    //           </IconButton>
    //           <ToolbarSeparator />
    //           <RaisedButton label="Login" primary onTouchTap={this.handleLoginOpen} />
    //           <IconMenu
    //             iconButtonElement={
    //               <IconButton touch>
    //                 <NavigationExpandMoreIcon />
    //               </IconButton>
    //           }
    //           >
    //             <MenuItem primaryText="Migration" />
    //             <MenuItem primaryText="Contact us" />
    //           </IconMenu>
    //         </ToolbarGroup>
    //       </Toolbar>
    //       <LoginModal
    //         open={this.state.loginModalOpen}
    //         onRequestClose={this.handleLoginClose}
    //       />
    //     </div>
    //   );
    // }
    // return (
    //   <Toolbar>
    //     <ToolbarGroup>
    //       <RaisedButton
    //         label={this.props.sideBarOpen ? 'Close' : 'Open'}
    //         onTouchTap={this.props.toggleFunc}
    //         primary
    //       />
    //       { !this.props.sideBarOpen ? (
    //         <a href="/">
    //           <img
    //             src={logoUrl}
    //             width="50"
    //             height="50"
    //             style={{ padding: 20 }}
    //             alt="SWD"
    //           />
    //         </a>
    //           ) : '' }
    //       <ToolbarTitle text="SWD" href="/" />
    //     </ToolbarGroup>
    //     <ToolbarGroup>
    //       <IconButton tooltip="Search Students" href="/search">
    //         <ActionSearch />
    //       </IconButton>
    //       <ToolbarSeparator />
    //       <RaisedButton label="Logout" primary />
    //       <Avatar
    //         src={logoUrl.default}
    //         size={45}
    //         style={{ margin: 5 }}
    //       />
    //       <IconMenu
    //         iconButtonElement={
    //           <IconButton touch>
    //             <NavigationExpandMoreIcon />
    //           </IconButton>

    //         }
    //       >
    //         <MenuItem primaryText="My Profile" />
    //         <MenuItem primaryText="Logout" />
    //       </IconMenu>
    //     </ToolbarGroup>
    //   </Toolbar>
    // );
  }
}

export default withApollo(Navigation);
