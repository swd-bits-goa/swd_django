
import React, { PropTypes } from 'react';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import TextField from 'material-ui/TextField';

class LoginModal extends React.Component {
  static propTypes = {
    open: PropTypes.bool.isRequired, // Handles modal state
    // Closure to allow child component to handle state data
    onRequestClose: PropTypes.func.isRequired,
  };

  login() {
    /* eslint class-methods-use-this: ["error", { "exceptMethods": ["login"] }] */
    // Code to submit login credentials
  }
  render() {
    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.props.onRequestClose}
      />,
      <FlatButton
        label="Login"
        primary
        keyboardFocused
        onTouchTap={this.login}
      />,
    ];

    return (
      <div>
        <Dialog
          title="Log In"
          actions={actions}
          modal={false}
          open={this.props.open}
          onRequestClose={this.props.onRequestClose}
        >
          Username same as BITS mail. Use your LDAP Authentication password to login.
          <br />
          <TextField
            floatingLabelText="Username"
          />
          <br />
          <TextField
            floatingLabelText="Password"
            type="password"
          />
          <br />
        </Dialog>
      </div>
    );
  }
}

export default LoginModal;
