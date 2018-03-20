import React from 'react';
import PropTypes from 'prop-types';
import Drawer from 'material-ui/Drawer';
import Menu from 'material-ui/Menu';
import MenuItem from 'material-ui/MenuItem';
import {Link} from "react-router-dom";
import logoUrl from '../Navigation/logo-small.png';
import {withRouter} from 'react-router-dom';
import profileIcon from './profile.svg';
import certificatesIcon from './certificates.svg';
import counselorIcon from './counselor.svg';
import contactsIcon from './contacts.svg';

const options = [
    {
      name: 'Profile',
      icon: profileIcon,
      link: ''
    },
    {
      name: 'Certificates',
      icon: certificatesIcon,
      link: ''
    },
    {
      name: 'Counselor',
      icon: counselorIcon,
      link: ''
    },
    {
      name: 'CSA',
      icon: counselorIcon,
      link: ''
    },
    {
      name: 'About SWD',
      icon: counselorIcon,
      link: '/aboutSWD'
    },
    {
      name: 'Contacts',
      icon: contactsIcon,
      link: ''
    }
];

class Sidebar extends React.Component {
  static propTypes = {
    open: PropTypes.bool.isRequired,
    toggleOpen: PropTypes.func.isRequired,
    history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  };
  

  handleMenuItemClick = (link) => {
    this.props.history.push(link);
    // Close the sidebar as soon as we've finished navigation
    this.props.toggleOpen()
  }

  render() {
    return (
      <div>
        <Drawer open={this.props.open} onRequestChange={this.props.toggleOpen} containerStyle={{marginTop: 55, backgroundColor: "#EDF1F2", width: "50%"}}>
          {
            options.map(option => 
    <MenuItem style={{paddingTop: 10}} onTouchTap={() => this.handleMenuItemClick(option.link)} key={option.name} ><img src={option.icon} style={{padding: 5, paddingRight: 10}}/> {option.name}</MenuItem>
  )
          }
        </Drawer>
        </div>
    );
  }
}

export default withRouter(Sidebar);

