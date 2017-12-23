import React from 'react';
import PropTypes from 'prop-types';
import Drawer from 'material-ui/Drawer';
import Menu from 'material-ui/Menu';
import MenuItem from 'material-ui/MenuItem';
import {Link} from "react-router-dom";
import logoUrl from '../Navigation/logo-small.png';

export default class Sidebar extends React.Component {
  static propTypes = {
    open: PropTypes.bool.isRequired,
  };

  // handleMenuItemClick = (event) => {
  //   console.log(event);

  // }

  render() {
    return (
        <Drawer open={this.props.open} style={{ zIndex: '-5000' }} zDepth={0} >
          <div style={{ width: '100%', textAlign: 'center' }}>
            <Link to="/">
              <img
                src={logoUrl}
                width="100"
                height="100"
                style={{ padding: 20 }}
                alt="SWD"
              />
            </Link>
          </div>
          <Menu>
          <Link to="/aboutSWD">
          <MenuItem >About SWD</MenuItem>
          </Link>
          <MenuItem>Menu Item 2</MenuItem>
          </Menu>
        </Drawer>
    );
  }
}
