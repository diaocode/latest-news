import clsx from 'clsx';
import Heading from '@theme/Heading';
import Translate from '@docusaurus/Translate';
import styles from './styles.module.css';

type FeatureItem = {
  title: JSX.Element;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: <Translate id="homepage.features.weibo.title">Social Media Trends</Translate>,
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        <Translate id="homepage.features.weibo.description">
          Track and analyze daily trending topics from Weibo, China's largest social media platform. 
          Stay informed about what's capturing public attention.
        </Translate>
      </>
    ),
  },
  {
    title: <Translate id="homepage.features.dailyupdates.title">Daily Updates</Translate>,
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        <Translate id="homepage.features.dailyupdates.description">
          Get fresh content daily with our curated blog posts and trending topics analysis. 
          Never miss important social discussions and news updates.
        </Translate>
      </>
    ),
  },
  {
    title: <Translate id="homepage.features.usefultools.title">Useful Tools</Translate>,
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        <Translate id="homepage.features.usefultools.description">
          Access our collection of practical tools including IT utilities and PDF tools. 
          Plus, enjoy some casual games in your free time.
        </Translate>
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
