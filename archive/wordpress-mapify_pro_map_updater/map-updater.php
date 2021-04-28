<?php /* Template Name: MapUpdater */ ?>
<?php

require get_template_directory() . "/map-updater/utils.php";
require get_template_directory() . "/map-updater/office.php";
require get_template_directory() . "/map-updater/inserter.php";


MapifyLocationsUpdater::update();
class MapifyLocationsUpdater {
  const INSERT_ONLY_FIRST_OFFICE_LOCATIONS = true;
  const HARD_INSERT = true;
  const OFFICES_LINK = "https://otc.kanga.exchange/data/offices.json";


  public static function update() {
    $json = file_get_contents( self::OFFICES_LINK );

    if ($json == null) return;

    $json_obj = json_decode( $json );
    $inserted_posts = array( 'inserted' => [] );

    if (!self::is_json_hash_equal_to_saved_hash( $json ) || self::HARD_INSERT) {
      self::delete_all_posts();

      Utils::update_stored_hash( hash( 'md5', $json ) );

      $inserter = new Inserter();

      foreach ($json_obj as $json_office_obj) {
        if (!Office::is_config_obj_valid( $json_office_obj )) continue;

        $office = new Office( $json_office_obj );

        $inserted_posts[ 'inserted' ] = array_merge(
          $inserted_posts[ 'inserted' ],
          $inserter->insert( $office->locations )
        );

        if (self::INSERT_ONLY_FIRST_OFFICE_LOCATIONS) break;
      }
    }

    self::print_pre( json_encode( $inserted_posts ) );
  }


  private static function delete_all_posts() {
    $existing_positions_query = Utils::get_map_locations();

    foreach ($existing_positions_query->posts as $post) {
      Utils::delete_map_locations( $post->ID, true );
    }
  }


  private static function is_json_hash_equal_to_saved_hash( $json ) {
    $saved_hash = Utils::get_stored_hash();
    $hash = hash( 'md5', $json );

    return $saved_hash == $hash;
  }


  private static function print_pre( $data ) {
    echo '<pre>';
    print_r( $data );
    echo '</pre>';
  }


  private static function print_json_offices( $json_obj ) {
    echo '<pre>';

    foreach ($json_obj as $json_office_obj) {
      $office = new Office( $json_office_obj );

      $office->print();
      echo "\n\n";
    }

    echo '</pre>';
  }
}