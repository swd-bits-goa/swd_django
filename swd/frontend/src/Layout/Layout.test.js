/* eslint no-undef: "off" */
// All the test utilties have been setup at /test/helpers.js

import React from 'react';
import getMuiTheme from 'material-ui/styles/getMuiTheme';
import App from '../App';
import Layout from './Layout';
import Header from '../Header';
import Footer from '../Footer';


const muiTheme = getMuiTheme({
  userAgent: navigator.userAgent,
});

describe('Layout', () => {
  let wrapper;
  before(() => {
    wrapper = mount(
      <App context={{ insertCss: () => {}, muiTheme }}>
        <Layout isLoggedIn>
          <div className="child" />
        </Layout>
      </App>,
    );
  });
  it('should render a Header', () => {
    expect(wrapper.containsMatchingElement(<Header />)).to.equal(true);
  });

  it('should render a Footer', () => {
    expect(wrapper.containsMatchingElement(<Footer />)).to.equal(true);
  });

  it('should render children correctly', () => {
    expect(wrapper.find('div.child').length).to.eq(1);
  });
});
