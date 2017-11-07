import React, { Component } from 'react'
import { BrowserRouter as Router, Route, Switch, Link } from 'react-router-dom'

import {
  ApolloProvider,
  ApolloClient,
  createBatchingNetworkInterface,
} from 'react-apollo'

import PropTypes from 'prop-types';

import CreateView from './views/CreateView'
import DetailView from './views/DetailView'
import ListView from './views/ListView'
import LoginView from './views/LoginView'
import LogoutView from './views/LogoutView'

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

class App extends React.PureComponent {

  getChildContext() {
    return this.props.context;
  }

  render() {
    // NOTE: If you need to add or modify header, footer etc. of the app,
    // please do that inside the Layout component.
    return React.Children.only(this.props.children);
  }

}

App.propTypes = {
  context: PropTypes.object.isRequired,
  children: PropTypes.element.isRequired,
};

App.childContextTypes = {
  insertCss: PropTypes.func.isRequired,
  muiTheme: PropTypes.object.isRequired,
};

// class App extends Component {
//   render() {
//     return (
//       <ApolloProvider client={client}>
//         <Router>
//           <div>
//             <ul>
//               <li><Link to="/">Home</Link></li>
//               <li><Link to="/messages/create/">Create Message</Link></li>
//               <li><Link to="/login/">Login</Link></li>
//               <li><Link to="/logout/">Logout</Link></li>
//             </ul>
//             <Route exact path="/" component={ListView} />
//             <Route exact path="/login/" component={LoginView} />
//             <Route exact path="/logout/" component={LogoutView} />
//             <Switch>
//               <Route path="/messages/create/" component={CreateView} />
//               <Route path="/messages/:id/" component={DetailView} />
//             </Switch>
//           </div>
//         </Router>
//       </ApolloProvider>
//     )
//   }
// }

export default App