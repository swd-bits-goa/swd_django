import React from "react";
import PropTypes from "prop-types";
import Drawer from "material-ui/Drawer";
import Menu from "material-ui/Menu";
import MenuItem from "material-ui/MenuItem";
import { Link } from "react-router-dom";
import logoUrl from "../Navigation/logo-small.png";
import { withRouter } from "react-router-dom";
import profileIcon from "./profile.svg";
import certificatesIcon from "./certificates.svg";
import counselorIcon from "./counselor.svg";
import contactsIcon from "./contacts.svg";
import Divider from "material-ui/Divider";
import s from "./Sidebar.css";
import { Avatar } from "material-ui";

const options = [
  {
    name: "Home",
    link: "/home"
  },
  {
    name: "My Account",
    link: "/profile"
  },
  {
    name: "Student Search",
    link: "/search"
  },
  {
    name: "About",
    link:
      "/aboutSWD" /* Note: This should be removed once the sub-menu links are completed */,
    submenus: [
      {
        name: "SWD",
        link: "/swd"
      },
      {
        name: "CSA",
        link: "/csa"
      },
      {
        name: "SAC",
        link: "/sac"
      }
    ]
  },
  {
    name: "Migration",
    link: "/Certificates" /* NOT WORKING */
  },
  {
    name: "Anti-Ragging",
    link: "/antiRagging" /* Not available now */
  },
  {
    name: "Contact Us",
    link: "/contactUs" /* Not available now */
  }
];

class Sidebar extends React.Component {
  constructor(props) {
    super(props);
    if (props.isLoggedIn) {
      this.generateLoggedInSubMenus();
    }
  }
  static propTypes = {
    open: PropTypes.bool.isRequired,
    toggleOpen: PropTypes.func.isRequired,
    isLoggedIn: PropTypes.bool.isRequired,
    history: PropTypes.shape({
      push: PropTypes.func.isRequired
    }).isRequired
  };

  handleMenuItemClick = link => {
    this.props.history.push(link);
    // Close the sidebar as soon as we've finished navigation
    this.props.toggleOpen();
  };

  generateMenuItem(link, keyName, customStyle) {
    const menuClass = customStyle || s.MenuItem;
    return (
      <MenuItem
        style={{ whiteSpace: "normal" }}
        className={menuClass}
        onTouchTap={() => this.handleMenuItemClick(link)}
        key={keyName}
      >
        {/* <img src={option.icon} style={{ padding: 5, paddingRight: 10 }} />{" "} */}
        {keyName}
      </MenuItem>
    );
  }

  generateLoggedInSubMenus() {
    const submenuMyAccount = [
      {
        name: "Mess Option",
        link: "/mess"
      },
      {
        name: "Leave",
        link: "/leave-application"
      },
      {
        name: "Events",
        link: "/events"
      },
      {
        name: "Dues",
        link: ""
      },
      {
        name: "Certificates",
        link: ""
      },
      {
        name: "Log out",
        link: "/logout"
      }
    ];

    options.forEach(option => {
      if (option.name === "My Account") option.submenus = submenuMyAccount;
    });
  }

  render() {
    const avatarLoggedOut = {
      height: 50,
      width: 50,
      marginTop: 20,
      marginBottom: 20
    };
    const avatarLoggedIn = {
      height: 50,
      width: 50,
      marginTop: 20,
      marginBottom: 20
    };
    const avatarText = {
      marginLeft: 10,
      color: "#C4C4C4"
    };
    return (
      <div>
        <Drawer
          open={this.props.open}
          docked={false}
          onRequestChange={this.props.toggleOpen}
          containerStyle={{
            backgroundColor: "#074F57",
            textAlign: "center",
            width: "50%"
          }}
        >
          {!this.props.isLoggedIn ? (
            <React.Fragment>
              <Avatar
                style={avatarLoggedOut}
                alt="Logged out"
                src={profileIcon}
              />
              <span style={avatarText}>Not Logged In</span>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <Avatar
                style={avatarLoggedIn}
                alt="Logged In"
                src={profileIcon}
              />
              <span style={avatarText}>Name</span>
            </React.Fragment>
          )}

          {options.map(option => {
            const MenuItemHeader = this.generateMenuItem(
              option.link,
              option.name
            );

            if (!option.submenus) {
              return MenuItemHeader;
            }

            const Items = [MenuItemHeader];
            option.submenus.forEach(submenu => {
              Items.push(
                this.generateMenuItem(submenu.link, submenu.name, s.SubMenuItem)
              );
            });
            return <React.Fragment>{Items}</React.Fragment>;
          })}

          <MenuItem
            style={{ whiteSpace: "normal" }}
            className={s.MenuItemFooter}
            key="footer"
          >
            &copy; Copyright 2018,
            <br />
            SWD Bits Goa Developers
          </MenuItem>
        </Drawer>
      </div>
    );
  }
}

export default withRouter(Sidebar);
