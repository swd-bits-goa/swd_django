/**
 * React Starter Kit (https://www.reactstarterkit.com/)
 *
 * Copyright © 2014-present Kriasoft, LLC. All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.txt file in the root directory of this source tree.
 */

import React, { PropTypes } from 'react';
import withStyles from 'isomorphic-style-loader/lib/withStyles';
import { BottomNavigation, BottomNavigationItem } from 'material-ui/BottomNavigation';
import Paper from 'material-ui/Paper';
import IconLocationOn from 'material-ui/svg-icons/communication/location-on';
// Import custom footer styles
import s from './Footer.css';


const nearbyIcon = <IconLocationOn />;

class Footer extends React.Component {
  static propTypes = {
    isLoggedIn: PropTypes.bool.isRequired,
  };

  state = {
    selectedIndex: 0,
  };

  select = index => this.setState({ selectedIndex: index });

  render() {
    if (!this.props.isLoggedIn) {
      return (
        <footer className={s.footer} >
          <div className={s.container}>
            <div>
              <h3 className={s.whiteText}>More</h3>
              <ul>
                <li><a className={s.whiteText} href="/swd-services">SWD Services</a></li>
                <li><a className={s.whiteText} href="/csa">CSA</a></li>
                <li><a className={s.whiteText} href="/activity-center">Activity Center</a></li>
              </ul>
            </div>
            <div>
              <h3 className={s.whiteText}>Connect</h3>
              <ul>
                <li><a className={s.whiteText} href="#!">Link 1</a></li>
                <li><a className={s.whiteText} href="#!">Link 2</a></li>
                <li><a className={s.whiteText} href="#!">Link 3</a></li>
                <li><a className={s.whiteText} href="#!">Link 4</a></li>
              </ul>
            </div>
            <div>
              <h3 className={s.whiteText}>Connect</h3>
              <ul>
                <li><a className={s.whiteText} href="#!">Contact Us</a></li>
                <li><a className={s.whiteText} href="#!">About Us</a></li>
                <li><a className={s.whiteText} href="#!">Link 3</a></li>
                <li><a className={s.whiteText} href="#!">Link 4</a></li>
              </ul>
            </div>
          </div>
          <div className={s.footerCopyright}>
            <span className={s.whiteText}>Developed By OSDLabs</span>
          </div>
        </footer>
      );
    }
    return (
      <Paper zDepth={1} style={{ bottom: 0, position: 'fixed', width: '100%' }}>
        <BottomNavigation selectedIndex={this.state.selectedIndex}>
          <BottomNavigationItem
            label="Location"
            icon={nearbyIcon}
            onTouchTap={() => this.select(0)}
          />
          <BottomNavigationItem
            label="Location"
            icon={nearbyIcon}
            onTouchTap={() => this.select(1)}
          />
          <BottomNavigationItem
            label="Location"
            icon={nearbyIcon}
            onTouchTap={() => this.select(2)}
          />
        </BottomNavigation>
      </Paper>
    );
  }
}

export default withStyles(s)(Footer);
