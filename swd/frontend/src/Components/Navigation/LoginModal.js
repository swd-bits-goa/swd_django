
import React from 'react';
import PropTypes from 'prop-types';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import TextField from 'material-ui/TextField';

class LoginModal extends React.Component {
  // to get token from django using REST framework
  handleSubmit(e) {
    e.preventDefault()
    let data = new FormData(this.form)
    fetch('http://localhost:8000/api-token-auth/', {
      method: 'POST',
      body: data,
    })
      .then(res => {
        res.json().then(res => {
          if (res.token) {
            localStorage.setItem('token', res.token)
            window.location.replace('/')
          }
        })
      })
      .catch(err => {
        console.log('Network error')
      })
  }

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
          modal={true}
          open={this.props.open}
          onRequestClose={this.props.onRequestClose}
        >
          Username same as BITS mail. Use your LDAP Authentication password to login.
          <form
          ref={ref => (this.form = ref)}
          onSubmit={e => this.handleSubmit(e)}
          >
          <div>
            <label>Username:</label>
            <input type="text" name="username" />
          </div>
          <div>
            <label>Password:</label>
            <input type="password" name="password" />
          </div>
        </form>
        </Dialog>
      </div>
    );
  }
}

export default LoginModal;
