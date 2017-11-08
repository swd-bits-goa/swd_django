import React, { Component } from 'react'
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom'
import {
  ApolloProvider,
  ApolloClient,
  createBatchingNetworkInterface,
} from 'react-apollo'
// import Layout from './Components/Layout';
import Footer from './Components/Footer';
import logo from './logo.svg';
import './App.css';
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

const client = new ApolloClient({
  networkInterface: networkInterface,
})

const Home1 = () => (
  <div className="App">
    <header className="App-header">
      <img src={logo} className="App-logo" alt="logo"/>
      <h1 className="App-title">Welcome to React</h1>
    </header>
    <p className="App-intro">
      To get started, edit
      <code>src/App.js</code>
      and save to reload.
    </p>
  </div>
);

class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
        <Route path="/footer" component={Footer}/>
        <Route path="/" component={Home1}/>
        
        </Switch>
      </Router>
    )
  }
}


export default App