
import React, { PropTypes } from 'react';
import { BottomNavigation, BottomNavigationItem } from 'material-ui/BottomNavigation';
import Paper from 'material-ui/Paper';
import IconLocationOn from 'material-ui/svg-icons/communication/location-on';
import {Mobile, Tablet} from '../Responsive';
// Import custom footer styles
import s from './Footer.css';


const nearbyIcon = <IconLocationOn />;

class Footer extends React.Component {
  // static propTypes = {
  //   isLoggedIn: PropTypes.bool.isRequired,
  // };

  state = {
    selectedIndex: 0,
  };

  select = index => this.setState({ selectedIndex: index });

  render() {
      return (
        <div>
        <Tablet>
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
        </Tablet>
      <Mobile>
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
    </Mobile>
    </div>
      )
}
}

export default (Footer);
