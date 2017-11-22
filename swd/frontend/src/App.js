import React, { Component } from 'react'
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom'
import {
  ApolloProvider,
  ApolloClient,
  createBatchingNetworkInterface,
} from 'react-apollo'
import Home from './Routes/home/Home';
import Layout from './Components/Layout';
import logo from './logo.svg';
import PropTypes from 'prop-types';
import injectTapEventPlugin from 'react-tap-event-plugin';

// react-tap-event-plugin provides onTouchTap() to all React Components.
// It's a mobile-friendly onClick() alternative for components in Material-UI,
// especially useful for the buttons.
injectTapEventPlugin();

const networkInterface = createBatchingNetworkInterface({
  uri: 'http://localhost:8000/gql',
  batchInterval: 10,
  opts: {
    credentials: 'same-origin',
  },
})

networkInterface.use([
  {
    applyBatchMiddleware(req, next) {
      if (!req.options.headers) {
        req.options.headers = {}
      }

      const token = localStorage.getItem('token')
        ? localStorage.getItem('token')
        : null
      req.options.headers['authorization'] = `JWT ${token}`
      next()
    },
  },
])

const client = new ApolloClient({
  networkInterface: networkInterface,
})


class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  componentDidCatch(error, info) {
    // Display fallback UI
    this.setState({ hasError: true });
    // You can also log the error to an error reporting service
    // logErrorToMyService(error, info);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
    loggedIn: true, //need to change this
    latestNews : [
  {
    title: 'Winner of Aditya Birla Group scholarship 2017',
    link: 'blah'
  }, {
    title: 'Important notice regarding MCN scholarship',
    link: 'blah'
  }
],
  };

  }

  render() {
    return (
      // apollo interfacing
      
      <ApolloProvider client={client}>
        <Router>
          <Switch>
          <Route path="/" render={ () => 
          (
            <Layout isLoggedIn={this.state.loggedIn}>
              
              <Home news={this.state.latestNews}/>
              </Layout>
          )}/>

          </Switch>
        </Router>
      </ApolloProvider>

    )
  }
}


export default App