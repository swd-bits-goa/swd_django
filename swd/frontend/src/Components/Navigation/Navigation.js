import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import bits from './bits.svg';
import swd from './swd.svg';
import line from './line.svg';
import s from './Navigation.css';

const styles = {
  root: {
    flexGrow: 1,
  },
  grow: {
    flexGrow: 1,
  },
  menuButton: {
    marginLeft: -12,
    marginRight: 20,
  },
  imgStyle: {
    marginRight: 10,
  },
};

function Navigation(props) {
  const { classes } = props;
  return (
    <div className={classes.root}>
      <AppBar position="static" color="white">
        <Toolbar>
          <IconButton className={classes.menuButton} color="inherit" aria-label="Menu">
            <MenuIcon />
          </IconButton>
          <img src={bits} height={44} alt="BITS Pilani Goa Campus" className={classes.imgStyle} />
          <img src={line} height={44} alt="divider" className={classes.imgStyle} />
          <img src={swd} height={44} alt="Student Welfare Division" />
          <div className={classes.grow} />
          <div className={classes.sectionDesktop}>
            <Button color="inherit" className={classes.navBut}>Home</Button>
            <Button color="inherit"className={classes.navBut}>Services</Button>
            <Button color="inherit"className={classes.navBut}>CSA</Button>
          </div>
          <div className={classes.sectionMobile}>
          </div>
        </Toolbar>
      </AppBar>
    </div>
  );
}

Navigation.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Navigation);