import React from 'react';
import PropTypes from 'prop-types';
import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import logoUrl from '../Navigation/logo-small.png';
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
      link: ''
    },
    {
      name: 'Contacts',
      icon: contactsIcon,
      link: ''
    }
];

export default class Sidebar extends React.Component {
  static propTypes = {
    open: PropTypes.bool.isRequired,
  };
  

  render() {
    return (
      <div>
        <Drawer open={this.props.open} containerStyle={{marginTop: 55}}>
          <Options options={options}/>
        </Drawer>
      </div>
    );
  }
}


const Options = ({options}) => {
  return options.map((option) => {
    return (<MenuItem style={{paddingTop: 10}}><img src={option.icon} style={{padding: 5, paddingRight: 10}}/> {option.name}</MenuItem>);
  });

}
