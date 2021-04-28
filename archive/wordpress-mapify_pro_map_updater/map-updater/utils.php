<?php

class Utils {
  public static function get_map_locations() {
    return new WP_Query( array( 'post_type' => 'map-location' ) );
  }


  public static function delete_map_locations( $map_id, $force ) {
    return wp_delete_post( $map_id, $force );
  }


  public static function get_stored_hash() {
    return get_option( 'JSON for Mapify converter hash', '' );
  }


  public static function update_stored_hash( $hash ) {
    return update_option( 'JSON for Mapify converter hash', $hash );
  }


  public static function insert_new_location( $props_array ) {
    return wp_insert_post( $props_array );
  }
}