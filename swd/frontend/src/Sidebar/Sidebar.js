import React, { PropTypes } from 'react';
import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';
import logoUrl from '../Navigation/logo-small.png';

export default class Sidebar extends React.Component {
  static propTypes = {
    open: PropTypes.bool.isRequired,
  };

  render() {
    return (
      <div>
        <Drawer open={this.props.open}>
          <div style={{ width: '100%', textAlign: 'center' }}>
            <a href="/">
              <img
                src={logoUrl}
                width="100"
                height="100"
                style={{ padding: 20 }}
                alt="SWD"
              />
            </a>
          </div>
          <MenuItem>Menu Item</MenuItem>
          <MenuItem>Menu Item 2</MenuItem>
        </Drawer>
      </div>
    );
  }
}
