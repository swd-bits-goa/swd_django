/* eslint react/jsx-no-bind: 0 */

import React from 'react';
import PropTypes from 'prop-types';
import { Card } from 'material-ui/Card';
import { List, ListItem } from 'material-ui/List';
import Divider from 'material-ui/Divider';
import withStyles from 'isomorphic-style-loader/lib/withStyles';
import s from './InfoCard.css';


const InfoCard = (props) => {
  const { title, list } = props;
  const navigateToLink = (link) => {
    window.location = link;
  };

  const listItems = list.map(element =>
    <div key={element.title}>
      <ListItem primaryText={element.title} onClick={navigateToLink.bind(null, element.link)} />
      <Divider />
    </div>,

    );
  return (
    <div className={s.container}>
      <span className={s.title}> {title} </span>
      <Card>
        <List>
          {listItems}
        </List>
      </Card>
    </div>
  );
};

InfoCard.propTypes = {
  title: PropTypes.string.isRequired,
  list: PropTypes.arrayOf(PropTypes.shape(
    { title: PropTypes.string,
      link: PropTypes.string },
    )).isRequired,
};

export default withStyles(s)(InfoCard);
