import React from 'react';
import PropTypes from 'prop-types';
import Responsive from 'react-responsive';

function Mobile(props) {
  return (
    <Responsive
      maxWidth={768} values={{
        deviceWidth: 700,
      }}
    >
      {props.children}
    </Responsive>
  );
}

Mobile.propTypes = {
  children: PropTypes.element.isRequired,
};

function Tablet(props) {
  return (
    <Responsive
      minWidth={768} values={{
        deviceWidth: 900,
      }}
    >
      {props.children}
    </Responsive>
  );
}

Tablet.propTypes = {
  children: PropTypes.element.isRequired,
};


export { Mobile, Tablet };
