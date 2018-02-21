import React from 'react';
import PropTypes from 'prop-types';
import Drawer from 'material-ui/Drawer';
import Menu from 'material-ui/Menu';
import MenuItem from 'material-ui/MenuItem';
import {Link} from "react-router-dom";
import logoUrl from '../Navigation/logo-small.png';
import {withRouter} from 'react-router-dom';

class Sidebar extends React.Component {
  static propTypes = {
    open: PropTypes.bool.isRequired,
    toggleOpen: PropTypes.func.isRequired,
    history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  };

  handleMenuItemClick = (event) => {
    var clickedItem = event.target.innerHTML
    switch(clickedItem)
    {
      case "About SWD":
        // Redirect
         this.props.history.push("/aboutSWD")
         break
      case "Menu Item 2":
        this.props.history.push("/")
        break;
      default:
        this.props.history.push("/")
    }
    // Close the sidebar as soon as we've finished navigation
    this.props.toggleOpen()
  }

  render() {
    return (
        <Drawer open={this.props.open} style={{ zIndex: '-5000' }} zDepth={0} >
          <div style={{ width: '100%', textAlign: 'center' }}>
              <img
                src={logoUrl}
                width="100"
                height="100"
                style={{ padding: 20 }}
                alt="SWD"
                onTouchTap={this.handleMenuItemClick}
              />
          </div>
          <Menu onItemTouchTap={this.handleMenuItemClick}>
          <MenuItem >About SWD</MenuItem>
          <MenuItem>Menu Item 2</MenuItem>
          </Menu>
        </Drawer>
    );
  }
}

export default withRouter(Sidebar)