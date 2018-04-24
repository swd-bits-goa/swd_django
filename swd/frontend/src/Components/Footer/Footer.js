
import React from 'react';
import PropTypes from "prop-types";
import { BottomNavigation, BottomNavigationItem } from 'material-ui/BottomNavigation';
import Paper from 'material-ui/Paper';
import {withRouter} from 'react-router-dom';
import ActionHome from 'material-ui/svg-icons/action/home';
import ActionEvent from 'material-ui/svg-icons/action/event';
import ActionProfile from 'material-ui/svg-icons/action/perm-identity';
import {Mobile, Tablet} from '../Responsive';
// Import custom footer styles
import s from './Footer.css';


const options = [
  {
    name: 'Home',
    icon: <ActionHome/>,
    link: '/'
  },
  {
    name: 'Profile',
    icon: <ActionProfile/>,
    link: '/profile'
  },  {
    name: 'Events',
    icon: <ActionEvent/>,
    link: '/events'
  }
];

class Footer extends React.Component {

  static contextTypes = {
    loggedIn: PropTypes.bool,
  };

  state = {
    selectedBottomNavIndex: options.findIndex(option => option.link === this.props.location.pathname)
  };

  handleBottomNavClick = (index, link) => {
    this.setState({ selectedBottomNavIndex: index })
    this.props.history.push(link);   
  }

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

        { this.context.loggedIn ?
      <Mobile>       
      <Paper zDepth={1} style={{ bottom: 0, position: 'fixed', width: '100%' }}>
        <BottomNavigation selectedIndex={this.state.selectedBottomNavIndex}>
        {
          options.map( (option, index) =>
          
            <BottomNavigationItem
            label={option.name}
            icon={option.icon}
            onTouchTap={() => this.handleBottomNavClick(index, option.link)}
            key={index}
          />
          )
        }
        </BottomNavigation>
      </Paper>
    </Mobile>
    : null
        }
    </div>
      )
}
}


export default withRouter(Footer);
